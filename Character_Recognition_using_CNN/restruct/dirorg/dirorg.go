package dirorg

import (
	"io/ioutil"
	"os"
	"path/filepath"
	"sync"
)

type (
	// DirOrg is the struct that wraps all methods needed to manipulate directories
	DirOrg struct {
		RootPath string
	}

	// FileInfoFP adds full path to fileInfo struct
	FileInfoFP struct {
		fullPath string
		os.FileInfo
	}

	toSend []*FileInfoFP

	adder func(os.FileInfo) bool
)

func checkDir(f os.FileInfo) bool {
	return f.IsDir()
}

func checkFile(f os.FileInfo) bool {
	return !checkDir(f)
}

//GetFilesDepth returns a list of files from a given level
func (dirorg *DirOrg) GetFilesDepth(depth int) ([]*FileInfoFP, error) {
	return dirorg.getFromDepth(depth, checkFile)
}

//GetDirectoriesDepth returns a list of directories from a given level
func (dirorg *DirOrg) GetDirectoriesDepth(depth int) ([]*FileInfoFP, error) {
	return dirorg.getFromDepth(depth, checkDir)
}

func (dirorg *DirOrg) getFromDepth(depth int, f adder) ([]*FileInfoFP, error) {
	currentPaths := []string{dirorg.RootPath}
	for i := 0; i < depth; i++ {
		currentPaths = getDirectoriesFrom(currentPaths).fullpaths()
	}

	return getFrom(currentPaths, f), nil
}

func getDirectoriesFrom(paths []string) toSend {
	return getFrom(paths, checkDir)
}

func getFrom(paths []string, f adder) []*FileInfoFP {
	fileChan := make(chan toSend)
	go visitor(paths, fileChan, f)
	return giveFound(fileChan)
}

func giveFound(receiver <-chan toSend) []*FileInfoFP {
	results := []*FileInfoFP{}
	for files := range receiver {
		results = append(results, files...)
	}
	return results
}

//
func visitor(visit []string, outer chan<- toSend, add adder) {
	var wg sync.WaitGroup
	for _, f := range visit {
		wg.Add(1)
		go func(path string, outChan chan<- toSend, wait *sync.WaitGroup) {
			defer wait.Done()
			files, err := digger(path, add)
			if err != nil {
				return
			}
			outChan <- files
		}(f, outer, &wg)
	}
	wg.Wait()
	close(outer)
}

func digger(from string, add adder) (toSend, error) {
	files, err := ioutil.ReadDir(from)
	if err != nil {
		return nil, err
	}

	result := make(toSend, 0)
	for _, f := range files {
		if add(f) {
			result = append(result, &FileInfoFP{
				fullPath: filepath.Join(from, f.Name()),
				FileInfo: f,
			})
		}
	}
	return result, nil
}

//GetAbsPath returns the absolute path of file
func (f *FileInfoFP) GetAbsPath() string {
	return f.fullPath
}

func (ts toSend) fullpaths() []string {
	r := make([]string, len(ts))
	for i := range ts {
		r[i] = ts[i].GetAbsPath()
	}
	return r
}
