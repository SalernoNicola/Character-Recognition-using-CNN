package main

import (
	"errors"
	"flag"
	"fmt"
	"log"
	"strconv"
	"time"

	"github.com/underscorefan/restruct/dirorg"
)

const (
	errMessageLess = "value must be greater than or equal to"
)

type programArgs struct {
	DirRoot      *string
	ToRoot       *string
	UntilDepth   *int
	FlattenDepth *int
	Split        *float64
	MaxFiles     *int
}

func lessOrErr(vl, dvl int, errMsg string) error {
	if vl < dvl {
		return errors.New(errMsg)
	}
	return nil
}

func simpleLOE(vl, dvl int, pre string) error {
	return lessOrErr(vl, dvl, errLessString(pre, dvl))
}

func errLessString(pre string, i int) string {
	return pre + " " + errMessageLess + " " + strconv.Itoa(i)
}

// argomenti passati a linea di comando
func parsedArgs() (*programArgs, error) {
	pa := &programArgs{
		DirRoot:      flag.String("root", ".", "directory root path"),
		ToRoot:       flag.String("to", "../copied", "directory in which you want to copy the restrucured dataset"),
		UntilDepth:   flag.Int("until", 1, "specify how deep the tool must go to find files"),
		FlattenDepth: flag.Int("flatten", 0, "specify how many steps up the files must be moved"),
		Split:        flag.Float64("split", 0.0, "specify the size of a block in which the dataset will be split"),
		MaxFiles:     flag.Int("maxfiles", 0, "specifiy the maximum number of elements to be taken from each subdirectory"),
	}

	flag.Parse()

	if err := simpleLOE(*pa.UntilDepth, 1, "until"); err != nil {
		return nil, err
	}

	if err := simpleLOE(*pa.FlattenDepth, 0, "flatten"); err != nil {
		return nil, err
	}

	if err := simpleLOE(*pa.MaxFiles, 0, "maxfiles"); err != nil {
		return nil, err
	}

	if err := lessOrErr(*pa.UntilDepth-*pa.FlattenDepth, 0, "'flatten' can't be greater than 'until'"); err != nil {
		return nil, err
	}

	if *pa.Split < 0 || *pa.Split > 1 {
		return nil, errors.New("split should be a value between 0 and 1")
	}

	return pa, nil
}

func main() {
	pa, err := parsedArgs()
	if err != nil {
		log.Fatalf("error: %s\n", err)
	}

	diro := &dirorg.DirOrg{
		RootPath: *pa.DirRoot,
	}

	copyUntil, err := diro.GetDirectoriesDepth(*pa.FlattenDepth)
	if err != nil {
		return
	}

	fmt.Println(">>> subdirectories found:")
	for _, cpd := range copyUntil {
		fmt.Println(">>> ", cpd.GetAbsPath())
	}

	// aku è la struct che contiene i metodi e gli attributi necessari affinché i dati vengano copiati nelle nuove directory
	aku := dirorg.NewAku(*pa.ToRoot, copyUntil)

	// creo le nuove directory e con lo split aggiungo un'ulteriore layer se il dataset deve essere diviso in
	// trainset e testset
	aku.CreateDirs(dirorg.Split(*pa.Split))

	reshaper := dirorg.NewReshaper(
		*pa.ToRoot, copyUntil,
		*pa.UntilDepth-*pa.FlattenDepth-1,
		*pa.MaxFiles,
		*pa.Split,
	)
	//fileTuples è un array di tuple
	n, tuples := time.Now(), make(chan dirorg.FileTuples)
	// il canale tuples viene utilizzato all'interno del metodo Boogie

	// goroutine
	go func() {
		reshaper.Boogie(tuples) //la forma delle tuples è (toRoot: string, copyUntil: string).
		close(tuples)
	}()

	// viene eseguito per ogni array di tuple inviato sul canale
	for el := range tuples {
		for _, tuple := range el {
			if err := aku.Copy(tuple); err != nil {
				log.Println(err)
			}
		}
	}
	//benchmark
	fmt.Println(time.Since(n))
}
