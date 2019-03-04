package dirorg

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"sync"
)

//DirWriter is used to copy files to a given directory
type (
	DirWriter struct {
		Root      string
		CopyDepth int
		Origins   []*FileInfoFP
	}
)

//NewDirWriter returns a pointer to DirWriter
func NewDirWriter(root string, baseCopy []*FileInfoFP, depth int) *DirWriter {
	return &DirWriter{
		Root:      root,
		Origins:   baseCopy,
		CopyDepth: depth,
	}
}

//Copy dir
func (dw *DirWriter) Copy() error {
	if err := dw.createRoot(); err != nil {
		return err
	}

	var wg sync.WaitGroup

	for _, dir := range dw.Origins {
		wg.Add(1)
		log.Println(">!> evaluating", dir.GetAbsPath())
		go func(d *FileInfoFP, w *sync.WaitGroup, dest string) {
			defer w.Done()
			dw.copyDir(d)
		}(dir, &wg, dw.Root)
	}

	// wg aspetta che il contatore delle goroutine arrivi a 0 (cioè che finiscano tutte le goroutine lanciate)
	wg.Wait()
	return nil
}

func (dw *DirWriter) createRoot() error {
	return createDir(dw.Root)
}

func (dw *DirWriter) copyDir(dir *FileInfoFP) error {
	files, err := (&DirOrg{
		RootPath: dir.GetAbsPath(),
	}).GetFilesDepth(dw.CopyDepth)
	if err != nil {
		return err
	}

	destDir := filepath.Join(dw.Root, dir.Name())
	if err := createDir(destDir); err != nil {
		return err
	}
	counter := 0
	for _, file := range files {
		err := copyFile(file.GetAbsPath(), filepath.Join(destDir, file.Name()))
		if err != nil {
			log.Println(err)
		}
		counter++
	}
	fmt.Println("copied " + strconv.Itoa(counter) + " files from " + dir.Name())
	return nil
}

// copia il file nell destinazione specificata in dst
func copyFile(src, dst string) error {
	b, err := ioutil.ReadFile(src)
	if err != nil {
		return err
	}

	return ioutil.WriteFile(dst, b, 0755)
}

// creo una directory
func createDir(dirPath string) error {
	return os.MkdirAll(dirPath, 0755)
}
