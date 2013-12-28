import subprocess


class Git(object):
    def __init__(self, workingdir=None):
        self.workingdir = workingdir
        self.devnull = open('/dev/null', 'w')

    def git_cmd(self, cmd):
        extra_args = []
        if self.workingdir:
            extra_args = [
                "--work-tree={0}".format(self.workingdir),
                "--git-dir={0}/.git".format(self.workingdir)
            ]
        return cmd + extra_args

    def git_call(self, cmd):
        return subprocess.call(
            self.git_cmd(cmd),
            stdout=self.devnull,
            stderr=subprocess.STDOUT
        )

    def git_output(self, cmd):
        return subprocess.check_output(
            self.git_cmd(cmd)
        ).strip()

    def git_lines(self, cmd):
        return [
            line for line in
            self.git_output(cmd).split('\n')
            if line.strip()
        ]

    def unstaged_changes(self):
        return self.git_lines(["git", "diff", "--name-only"])

    def uncommited_changes(self):
        return self.git_lines(
            ["git", "diff", "--name-only", "--cached"]
        )

    def untracked_files(self):
        return self.git_lines(
            ["git", "ls-files", "--other", "--exclude-standard", "--directory"]
        )

    def commit_id(self):
        return self.git_output(["git", "rev-parse", "HEAD"])


if __name__ == "__main__":
    git = Git()
    print git.unstaged_changes()
    print git.uncommited_changes()
    print git.untracked_files()
    print git.commit_id()
