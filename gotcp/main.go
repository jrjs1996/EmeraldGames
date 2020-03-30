package main

import (
	"bufio"
	//"database/sql"
	"fmt"
	"net"
	"os"
	"strings"
)
import _ "github.com/go-sql-driver/mysql"

func main() {
	// Should switch protocol to unix domain socket?
	/*
	db, err := sql.Open("mysql", "djangop:testpassword@/mysql")
	if err != nil {
		fmt.Println(err)
		return
	}
	defer db.Close()
	rows, err := db.Query("SELECT * FROM main_sandboxplayer")
	if err != nil {
		fmt.Println(err)
		return
	}
	defer rows.Close()
	for rows.Next() {
		var (
			id int
			name string
			date string
			balance string
			password string
			game_id string
		)
		err := rows.Scan(&id, &name, &date, &balance, &password, &game_id)
		if err != nil {
			fmt.Println(err)
		}
		fmt.Println(id, name, date, balance, password, game_id)
	}
	db.Close()
	*/
	args  := os.Args
	if len(args) == 1 {
		fmt.Println("Please provide port number")
		return
	}
	PORT := "0.0.0.0:" + args[1]
	l, err := net.Listen("tcp4", PORT)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer l.Close()
	fmt.Println("Listening...")
	for {
		c, err := l.Accept()
		if err != nil {
			fmt.Println(err)
			return
		}
		go handleConnection(c)
	}
}

func handleConnection(c net.Conn) {
	fmt.Printf("Serving %s\n", c.RemoteAddr().String())
	for {
		netData, err := bufio.NewReader(c).ReadString('\n')
		if err != nil {
			fmt.Println(err)
			return
		}

		temp := strings.TrimSpace(string(netData))
		fmt.Println(netData)
		if temp == "STOP" {
			fmt.Println("Received stop")
			break
		}
		c.Write([]byte{FIRST, SECOND, THIRD})
	}
	c.Close()
}


const FIRST uint8 = 0
const SECOND uint8 = 1
const THIRD uint8 = 2

const ACTION_ABORT_MATCH uint8 = 0
const ACTION_ADD_PLAYER_TO_GROUP uint8 = 1
const ACTION_CREATE_MATCH uint8 = 2
const ACTION_CREATE_PLAYER_GROUP uint8 = 3
const ACTION_CREATE_SOLO_PLAYER_GROUP uint8 = 4
const ACTION_END_MATCH uint8 = 5
const ACTION_MATCH_INFO  uint8 = 6
const ACTION_OBTAIN_AUTH_TOKEN uint8 = 7
const ACTION_PLAYER_INFO uint8 = 8
const ACTION_PLAYER_QUIT uint8 = 9
const ACTION_REMOVE_PLAYER_GROUP  uint8 = 10
const ACTION_START_MATCH uint8 = 11
