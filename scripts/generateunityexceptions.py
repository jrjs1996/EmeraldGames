

with open("./main/exceptions.py", "r") as exceptions:
    with open("emeraldexceptions.txt", "w") as emeraldExceptions:
        name = ""
        for line in exceptions:
            if line.startswith("class"):
                name = line[line.find(" ")+1:line.find("(")]
            elif "self.code" in line:
                line = line.strip()
                code = line[line.find(" = ") + 3:]
                emeraldExceptions.write("public class " + name + " : EmeraldException\n"
                                        "{\n"
                                        "   public new static int code = " + code + ";\n"
                                        "   public " + name + "(string message) : base(message) { }\n"
                                        "}\n\n")
