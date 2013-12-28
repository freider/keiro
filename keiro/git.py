import subprocess


class Git(object):
    def __init__(self, workingdir=None):
        self.workingdir = workingdir
        self.devnull = open('/dev/null', 'w')

    def git_cmd(self, cmd):
        base = ["git"]
        if self.workingdir:
            base += [
                "--work-tree={0}".format(self.workingdir),
                "--git-dir={0}/.git".format(self.workingdir)
            ]
        return base + cmd

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
        return self.git_lines(["diff", "--name-only"])

    def uncommited_changes(self):
        return self.git_lines(
            ["diff", "--name-only", "--cached"]
        )

    def untracked_files(self):
        return self.git_lines(
            ["ls-files", "--other", "--exclude-standard", "--directory"]
        )

    def commit_id(self):
        return self.git_output(["rev-parse", "HEAD"])


if __name__ == "__main__":
    git = Git(".")
    print git.unstaged_changes()
    print git.uncommited_changes()
    print git.untracked_files()
    print git.commit_id()
