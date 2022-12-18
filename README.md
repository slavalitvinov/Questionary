# Questionary

A tool to present questionaries.

# Input format

Questions are grouped into a consequent group of text lines. An empty line (or many) separate the questions.

The first line from the top or after an empty line is a question.

The following lines declare answers.

An answer that starts with "*" symbol is the correct answer.

An answer can include an image reference. Image filename (relative to the questionary file) should
be declared in squared brackets ([filename.jpg]). The following text is considered an answer.

Additionally, there could be a line start with '>'. It indicates the final message which can provide
more details about the question or the answer. The line can include an optional image reference
and text in the same format as the answer.

Example:

```
How many colors are in rainbow?
3
5
6
* 7
> [rainbow.jpg] Rainbow colors are red, orange, yellow, green, blue, indigo, violet
```

