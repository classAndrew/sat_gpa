package main

import (
	"log"
	"math/rand"

	"github.com/gin-gonic/gin"
)

// test go server
func main() {
	r := gin.Default()
	r.GET("/random", func(c *gin.Context) {
		p := make([]byte, 49152*8)
		if _, err := rand.Read(p); err != nil {
			log.Fatalln(err.Error())
			c.JSON(500, gin.H{"error": err.Error()})
		}

		c.JSON(200, gin.H{"data": string(p) + "abcdefghijklmnopqrstuvwxyz"})
	})
	r.Run(":8000")
}
