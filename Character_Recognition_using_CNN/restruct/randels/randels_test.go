package randels

import (
	"testing"
)

func TestRandels(t *testing.T) {
	p := Picker{
		Max:   100,
		Range: 10,
	}
	p.For(func(i, g int) {
		println(i, g)
	})

	a := Picker{
		Max:   50,
		Range: 51,
	}
	a.For(func(i, g int) {
		println(i, g)
	})
}
