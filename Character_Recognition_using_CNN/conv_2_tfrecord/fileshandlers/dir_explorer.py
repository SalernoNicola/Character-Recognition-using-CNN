import os


class DirectoryExplorer:
    MIN_SUBDIRS = 2

    # maybe  check root over here, and avoid passing dirs
    def __init__(self, root,  file_extensions=('.png', '.jpeg', '.jpg')):
        if not os.path.exists(root):
            raise IOError(self.__init_error(root) + 'doesn\'t exist')

        if not os.path.isdir(root):
            raise ValueError(self.__init_error(root) + 'is not a directory')

        directories = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
        if len(directories) < self.MIN_SUBDIRS:
            raise ValueError(self.__init_error(root) + 'doesn\'t contain enough subdirectories {' +
                             str(self.MIN_SUBDIRS) + '}')

        self.dirs = directories
        self.root = root
        self.accepted_extensions = file_extensions

    def add_dir(self, cto):
        self.dirs.append(cto)

    def only_valid_ext(self, actual_directory):
        return [f.endswith(self.accepted_extensions) for f in self.__rls(actual_directory)].count(False) == 0

    def get_files_from(self, ad):
        return [os.path.join(self.root, ad, f) for f in self.__rls(ad) if f.endswith(self.accepted_extensions)]

    def get_abs_paths(self):
        return [os.path.join(self.root, d) for d in self.dirs]

    def __rls(self, ad):
        return os.listdir(os.path.join(self.root, ad))

    @staticmethod
    def __init_error(path):
        return 'specified path {' + path + '} '
