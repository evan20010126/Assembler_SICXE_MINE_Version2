# SIC/XE Version2

## 檔案介紹
- 主要執行的檔案有
  1. assembler.py: 
    > 為主程式
  2. sic.py: 
    > 紀錄sic/xe的指令與對應的opcode和相應的instruction format
  3. sicasmparser.py
    > 將讀進來的.asm檔案，拆成三個部分: (label, opcode, oprand)
  4. objfile.py
    > 將準備好要寫入.obj的文字準備好後，並存入.obj
  
  :alien:備註: 測試的.asm檔案放在"asm_Language_for_testing"資料夾內:alien:
