# Breakthrough Game – Data Structures and Algorithms

This project is an implementation of the **Breakthrough** board game in Python.  
It uses custom data structures and includes an AI opponent powered by **minimax search** with **alpha-beta pruning**, **heuristic evaluation**, and **Zobrist hashing** for transposition tables.

----

## 🎮 About the Game
**Breakthrough** is a two-player strategy board game.  
The goal is to **move one of your pawns to the opponent’s back rank** or prevent your opponent from making any legal moves.  

- The board is **8x8**.  
- Each player starts with two rows of pawns.  
- **White pawns** move upward, **Black pawns** move downward.  
- Pawns can move:
  - Forward into an empty square  
  - Diagonally forward to capture an opponent’s pawn and also into an empty square 

---

## ⚙️ Features
- Full game implementation with move validation  
- AI opponent with:
  - Minimax search and alpha-beta pruning  
  - Transposition table with Zobrist hashing  
  - Custom heuristic evaluation function  
- Human vs AI gameplay (choose White or Black)  
- ASCII-based board visualization in the terminal  

---

## 🛠️ Requirements
- Python 3.8+  
- Custom `data_structures` module (Stack, DynamicArray, DoubleList, ChainHashMap, Tree, HeapPriorityQueue)  

---
Clone the repository:
   ```bash
   git clone https://github.com/Rikiccc/breakthrough_game.git
   cd breakthrough_game
