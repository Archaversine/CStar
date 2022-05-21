# C* Documentation

Disclaimer: If you have any value for time, practicality, or anything of the like, **this is not for you**.

## C* Tape

Unless specified, the program begins with a 'tape' of 8 bytes that can have values ranging from 0-255 all initialized to 0,
starting at the first byte of the tape. When the shell mode of C* is used, the contents of the entire tape are printed out 
to the screen after every command. If the default tape is not sufficent for a program, it can be reset in the following ways:

Initializing tape to a size of three all initialized to 0:
```
# 0 0 0
```

Initializing tape to the ASCII values of "Hello, World!" with a newline at the end in hexadecimal:
```
# 0x48 0x65 0x6c 0x6c 0x6f 6x2c 0x20 0x57 0x6f 0x72 0x6c 0x64 0x21 0xa
```

Initializing tape to ASCII values of "Hello, World!" with a newline at the end in decimal:
```
# 72 101 108 108 111 44 32 87 111 114 108 100 33 10
```

Initializing tape to ASCII values of "Hello, World!" with a newline at the end via string notation:
```
"Hello, World!\n"
```

## Modifying the Tape's Position

By default, the tape position is set to 0, which is the left-most or first value of the tape. To change the position of the tape, 
the following symbols can be used:

| Symbol | What it does |
| --- | --- |
| `->` | Increase the tape's position by 1 (move right 1). |
| `<-` | Decrease the tape's position by 1 (move left 1). |
| `>>` | Set the tape's position to the end of the tape (right-most value). |
| `<<` | Set the tape's position to the beginning of the tape (left-most value). |

## Modifying the Current Cell's Value

There are three basic operations that can modify the value of the selected cell on the tape:

### \[`+`\] Increase Value

Using `+` followed by a number will increase the cell's value by that amount. If the result exceeds 255 or 0xff, an overflow will occur.

Increase cell value by 1:
```
+1
```

Increase cell value by 0x1f:
```
+0x1f
```

### \[`-`\] Decrease Value

Using `-` followed by a number will decrease the cell's value by that amount. If the result is less than 0, an underflow will occur.

Decrease cell value by 1:
```
-1
```

Decrease cell value by 0x1f:
```
-0x1f
```

### \[`~`\] Override Value

Using `~` followed by a number will override the cell's current value to the specified amount. If the value is not in the range 0-255 
then either an underflow or overflow will occurr.

Set the cell's value to 8
```
~8
```

Set the cell's value to 255 via underflow
```
~-1
```

## Input and Output Operations

Input and Output in C* is done char-by-char unless the program specifies to read a number. If the user types more than what is requested, then
the remaining chars are stored into a char buffer. If the char buffer has chars, then char input operations will take chars from the char buffer
rather than the user. Below are the input output operations:

| Symbol | What it does |
| --- | --- |
| `=>` | Read a char from either the user or the char buffer |
| `<=` | Convert the current cell's value into an ASCII character and display it to the screen. |
| `%>` | Read an integer from the user (does not read from the char buffer) |
| `<%` | Display the current cell's value as an integer. |
| `<>` | Shorthand for `<= ->`. |
| `<%>` | Shorthand for `<% ->`. |

## Control Flow

### Hard-Coded Loops

It is sometimes difficult to write the same sequence of symbols over and over again, and greatly increases the risk of bugs and errors.
To combat this, a hard coded loop using `[]` can be used.

The syntax for a hard-coded loop is as follows:
```
[iterations](...symbols...)
```

Note that if only one symbol is going to be repeated, then the parenthesis are not needed. 
Also note that C* does not currently support nested parenthesis (there are workarounds that will be shown later on).

If the number of iterations is equal to 0, then the loop will run as many times as there are cells in the tape.
Any number less than 0 will run `len(tape) - 1` times.

The following code will print the current char and move right 5 times:
```
[5](<= ->)
```

The following code will print the current char 5 times **then** move right:
```
[5]<= ->
```

The following code will add 1 to the current cell `len(tape)` times:
```
[0]+1
```

The following code will print the current char and move right `len(tape) - 1` times:
```
[-1](<= ->)
```

### Conditional Operators

There are five conditional operators that can be used to control the flow of code. They follow the same parenthesis syntax as hard-coded loops.

| Symbol | What it does |
| --- | --- |
| `?` | Runs as long as the current cell does not have a value of 0. |
| `!?` | Runs as long as the current cell has a value of 0. |
| `??` | Runs **once** if the current cell does not have a value of 0. |
| `!??` | Runs **once** of the current cell has a value of 0. |
| `C?` | Runs as long as there are characters in the char buffer. |

The following code will decrement the current cell's value until it is equal to 0:
```
?-1
```

The following code decrements the current cell's value and increments it's right neighbor until it is equal to 0:
```
?(-1 -> +1 <-)
```

The following code will set the cell's current value to 1 if it has a nonzero value:
```
??~1
```

The following code will read a string from the user:
```
=> -> C?(=> ->)
```

### Jump Points

Cell's can be 'bookmarked' to travel to them easier. The syntax is as follows:
```
@name
^name
```
The first line will set the bookmark, and the second line will set the tape position to the bookmarked cell.

The following code will bookmark the current cell as `begin`, travel right until it reaches a zero value, bookmark that cell as `end`,
then jump back to `begin`:
```
@begin ?(->) @end ^begin
```

### Functions

If a piece of code is used over and over again but not in the same spot, or you need to nest parenthesis, then a function should be used.
Functions are defined with the syntax:
```
&func_name(...code...)
```

And can be called with the syntax:
```
*func_name
```

When `func_name` is called using the `*` symbol, then `...code...` will run. 

Below is a function that sets the current cell's value to 1 if it has a nonzero value and sets it to 255 if it has a zero value.
The function will only run if the curent cell has a nonzero value (this is a useless function but shows how to avoid nested parenthesis):
```
&func(??~1 !??~255)

??(*func)
```

Functions may call other functions in their definitions.


## Map, Table operators (`{}` and `{{}}`)

### Map Operator `{}`

The map operator can be used to map a value of a cell to a different value depending on the value.

The syntax:
```
{fromValue1:toValue1,fromValue2:toValue2, ... ,::defaultValue}
```

The map can have as may from-to pairs as needed, and the default value is optional.

The following code maps the number 0 to 1, and 1 to 0:
```
{0:1,1:0}
```

This can be used to negate a cell's value, if it is equal to 1 or 0. To account for the cell being another value, the default value can be used.
This changes the syntax to:
```
{0:1,1:0,::0}
```

### Table Operator `{{}}`

The table operator is almost identical to the map operator, except double braces are used and instead of mapping numbers to other numbers,
it maps numbers jump points that have been made.

The following code jumps to the bookmark `begin` if the value is 0, `end` if the value is 1, and `other` if the value is not 1 or 0:
```
{{0:begin,1:end,::other}}
```

