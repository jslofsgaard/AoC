from typing import Callable


TOTAL_DISK_SPACE = 70000000
REQUIRED_FREE_SPACE = 30000000


class File:
    """Rerpresents a file found on the device's file system."""

    def __init__(self, size: int, name: str):
        self.name = name
        self.size = int(size)

    def __str__(self):
        return f"- {str(self.name)}: {self.size}"


class Directory:
    """Represents a directory found on the device's file system."""

    def __init__(
        self,
        name: str,
        parent: "Directory | None",
    ):
        self.name = name
        self.parent = parent
        self.children = []
        self.files = []

    @property
    def size(self) -> int:
        if len(self.files) == 0 and len(self.children) == 0:
            return 0

        return sum(map(lambda d: d.size, self.children)) + sum(
            map(lambda f: f.size, self.files)
        )

    @property
    def path(self) -> str:
        path = f"{self.name}/"
        parent = self.parent
        while parent is not None:
            path = parent.name + "/" + path
            parent = parent.parent

        return path

    def __str__(self):
        return f"d {str(self.name)}: {str(self.size)}"

    def get_child(self, name: str) -> "Directory":
        """Return the subdirectory with the provided name if it exists."""
        for child in self.children:
            if child.name == name:
                return child

    def populate(self, listings: tuple[str, str]) -> None:
        """Provided a listing of input as produced in the device's terminal,
        populate a directory with the corresponding contents.
        """
        for listing in listings:
            if listing[0] == "dir":
                self.children.append(Directory(listing[1], self))
            else:
                self.files.append(File(*listing))

    def ls(self, R: bool = False) -> None:
        """Print the contents of the directory.

        With the optional R flag, print the contents of all subdirectories.
        """
        print(f"{self.path}:")
        for child in self.children:
            print(str(child))

        for file in self.files:
            print(str(file))

        if R:
            print()
            for child in self.children:
                child.ls(R=True)


def find_subdirectories(
    predicate: Callable[[Directory], bool], directory: Directory
) -> list[Directory]:
    """Returns a list of all directories below and including directory
    which satisfy the predicate function.
    """
    dirs = []
    for child in directory.children:
        dirs += find_subdirectories(predicate, child)

    if predicate(directory):
        return [directory] + dirs
    else:
        return dirs


def cd(
    cwd: Directory,
    arg: str,
) -> Directory:
    """Return the new cwd for the provided arg.

    If cwd is none, create the root directory.
    """
    if cwd is None:
        return Directory("", None)

    if arg == "..":
        return cwd.parent

    return cwd.get_child(arg)


def get_directory_tree(puzzle_input: str = "input.txt") -> Directory:
    """Parse the puzzle input and return the root directory of the
    corresponding directory tree.
    """

    def get_root(cwd: Directory) -> Directory:
        if cwd.parent is None:
            return cwd

        return get_root(cwd.parent)

    cwd = None
    with open("input.txt") as f:
        line = f.readline()
        while line != "":
            command = line.split()[1]
            if command == "cd":
                cwd = cd(cwd, line.split()[2])
                line = f.readline()
            else:
                listings = []
                line = f.readline()
                while line != "" and line[0] != "$":
                    listings.append(tuple(line.split()))
                    line = f.readline()

                cwd.populate(listings)

    return get_root(cwd)


if __name__ == "__main__":
    root = get_directory_tree()
    small_dirs = find_subdirectories(lambda d: d.size < 100000, root)
    print(
        (
            f"There are {str(len(small_dirs))} directories "
            "with size less than 100000.\n"
            f"Their total size is: {sum(map(lambda d: d.size, small_dirs))}."
        )
    )

    unused_space = TOTAL_DISK_SPACE - root.size
    amount_to_delete = REQUIRED_FREE_SPACE - unused_space
    deleteable_dirs = sorted(
        find_subdirectories(lambda d: d.size > amount_to_delete, root),
        key=lambda d: d.size,
    )
    print(
        (
            "The smallest directory we can delete to free up enough space is: "
            f"{deleteable_dirs[0].path}\n"
            f"Its size is: {deleteable_dirs[0].size}."
        )
    )
    print("Its contents are:")
    deleteable_dirs[0].ls(True)
