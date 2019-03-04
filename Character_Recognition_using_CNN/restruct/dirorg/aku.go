package dirorg

import (
	"path/filepath"
)

//Aku holds all the data needed to create and copy files
// base string = toRoot radice nuova cartella, sroots=copyUntil l'albero delle sottocartelle
type Aku struct {
	base   string
	sroots []*FileInfoFP
}

// NewAku is used to create a new aku instance
func NewAku(base string, sroots []*FileInfoFP) *Aku {
	return &Aku{
		base:   base,
		sroots: sroots,
	}
}

// CreateDirs creates dirs
func (aku *Aku) CreateDirs(split bool) {
	if split {
		aku.both()
		return
	}
	aku.preserve()
}

// viene utilizzata per creare dirs
func (aku *Aku) preserve() {
	for _, groot := range aku.sroots {
		createDir(filepath.Join(aku.base, groot.Name()))
	}
}

func (aku *Aku) both() {
	for _, groot := range aku.sroots {
		createDir(filepath.Join(aku.base, b, groot.Name()))
		createDir(filepath.Join(aku.base, s, groot.Name()))
	}
}

//Copy return sorgente e destinazione
func (aku *Aku) Copy(t *FileTuple) error {
	return copyFile(t.GetSource(), t.GetDest())
}
