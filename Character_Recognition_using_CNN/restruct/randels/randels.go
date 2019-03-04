package randels

import (
	"math/rand"
	"time"
)

//Picker defines the range and the max number to be generated
type Picker struct {
	Max   int
	Range int
}

//For is a method that allows iteration while numbers are generated
func (p *Picker) For(iter func(index, gen int)) {
	src := rand.NewSource(time.Now().UnixNano())
	comodo := make(map[int]bool)
	for i := 0; i < p.Range; {
		if k := int(src.Int63()) % p.Max; !comodo[k] {
			iter(i, k)
			comodo[k] = true
			i++
		}
	}
}
