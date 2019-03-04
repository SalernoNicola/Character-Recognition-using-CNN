package dirorg

import (
	"fmt"
	"math"
	"path/filepath"
	"sync"

	"github.com/underscorefan/restruct/randels"
)

const (
	b = "big"
	s = "small"
)

type (

	//Reshaper holds all the data needed to copy files, it is attached to methods used to create a list of tuples
	//of the form: (sourcePath string, destinationPath string)
	Reshaper struct {
		BaseDirectory string
		CopyDepth     int
		SubRoots      []*FileInfoFP
		MaxFiles      int
		Split         float64
	}

	//FileTuple is an utility struct used to hold source and destination paths to copy
	FileTuple struct {
		source string
		dest   string
	}

	//FileTuples is an alias for an array of FileTuple pointers
	FileTuples []*FileTuple

	destMaker interface {
		makePath(originalFile string, add int) string
	}

	simpleDestMaker struct {
		dir string
	}

	prefixDestMaker struct {
		oneor                    map[int]bool
		dir, firstsub            string
		secondsub, subRoot, root string
	}
)

//NewReshaper returns a reference to Reshaper
func NewReshaper(root string, baseCopy []*FileInfoFP, depth int, mf int, split float64) *Reshaper {
	return &Reshaper{
		BaseDirectory: root,
		SubRoots:      baseCopy,
		CopyDepth:     depth,
		MaxFiles:      mf,
		Split:         split,
	}
}

//Boogie lancia le goroutine per un range di subRoots reshaper
func (reshaper *Reshaper) Boogie(conn chan<- FileTuples) error {
	var wg sync.WaitGroup
	for _, subRoot := range reshaper.SubRoots {
		wg.Add(1)
		fmt.Println("started ", subRoot)
		go func(sub *FileInfoFP) {
			files, _ := fetchFiles(sub.GetAbsPath(), reshaper.CopyDepth)
			toPick, maxNumber := reshaper.parameters(len(files))
			picked := make([]*FileInfoFP, toPick)
			iterator := randels.Picker{
				Max:   maxNumber,
				Range: toPick,
			}
			iterator.For(func(iter, gen int) {
				picked[iter] = files[gen]
			})
			conn <- reshaper.createTuples(picked, sub.Name()) // invia i dati sul canale
			wg.Done()
		}(subRoot)
	}
	// aspetta che treminino tutte le goroutine lanciate
	wg.Wait()
	return nil
}

func (reshaper *Reshaper) splitIt() bool {
	return Split(reshaper.Split)
}

//Split is an utility function to check whether the ds needs to be split in two
func Split(s float64) bool {
	return s > 0.0 && s < 1.0
}

// restituisce le tuples formate da sorgente e destinazione
func (reshaper *Reshaper) createTuples(files []*FileInfoFP, subRoot string) FileTuples {
	nfiles := len(files)
	tuples := make(FileTuples, nfiles)

	dm := reshaper.newDestMaker(subRoot, nfiles)
	for i, file := range files {
		tuples[i] = &FileTuple{
			source: file.GetAbsPath(),
			dest:   dm.makePath(file.Name(), i),
		}
	}
	return tuples
}

func (reshaper *Reshaper) parameters(nfiles int) (int, int) {
	if reshaper.MaxFiles <= 0 || reshaper.MaxFiles >= nfiles {
		return nfiles, nfiles
	}
	return reshaper.MaxFiles, nfiles
}

func (reshaper *Reshaper) getMinBlock(num float64) int {
	r := math.RoundToEven(num * reshaper.Split)
	return int(math.Min(r, num-r))
}

func fetchFiles(abspath string, depth int) ([]*FileInfoFP, error) {
	return (&DirOrg{
		RootPath: abspath,
	}).GetFilesDepth(depth)
}

// restituisce una mappa di indici
func generateIndexMap(max, niter int) map[int]bool {
	indexes := make(map[int]bool, niter)
	iterator := randels.Picker{
		Max:   max,
		Range: niter,
	}
	iterator.For(func(index, generated int) {
		indexes[generated] = true
	})

	return indexes
}

func minmax(al []int) (int, int, bool) {
	if len(al) == 0 {
		return 0, 0, false
	}
	min := al[0]
	max := al[0]

	for _, el := range al {
		if el < min {
			min = el
		}
		if el >= max {
			max = el
		}
	}
	return min, max, true
}

// se è possibile fare lo splitIt allora restituisco la struttura con s e b.
// Altrimenti restituisco la struttura semplice
func (reshaper *Reshaper) newDestMaker(subRoot string, nfiles int) destMaker {
	if reshaper.splitIt() {
		min := reshaper.getMinBlock(float64(nfiles))
		return &(prefixDestMaker{
			oneor:     generateIndexMap(nfiles, min),
			firstsub:  s, // small
			secondsub: b, // big
			root:      reshaper.BaseDirectory,
			subRoot:   subRoot,
		})
	}
	return &(simpleDestMaker{
		dir: filepath.Join(reshaper.BaseDirectory, subRoot),
	})
}

// simpleDestMaker è una struttura con solo dir string
func (sdm *simpleDestMaker) makePath(file string, add int) string {
	return filepath.Join(sdm.dir, file)
}

func (pdm *prefixDestMaker) makePath(file string, add int) string {
	if pdm.oneor[add] {
		return pdm.realpath(pdm.firstsub, file)
	}
	return pdm.realpath(pdm.secondsub, file)
}

func (pdm *prefixDestMaker) realpath(sub, file string) string {
	return filepath.Join(pdm.root, sub, pdm.subRoot, file)
}

//GetSource retrieves the source path
func (ft *FileTuple) GetSource() string {
	return ft.source
}

//GetDest retrieves the destination path
func (ft *FileTuple) GetDest() string {
	return ft.dest
}
