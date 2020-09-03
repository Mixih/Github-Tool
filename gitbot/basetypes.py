class RepoOrgBase:

    def collect_members(self, team=None):
        raise NotImplementedError

    def collect_repos(self):
        raise NotImplementedError

    def check_member(self, username):
        raise NotImplementedError

    def check_repo(self, reponame):
        raise NotImplementedError

    def add_member(self, username, role='member', team=None):
        raise NotImplementedError

    def add_private_repo(self, name):
        raise NotImplementedError

    def add_user_to_repo(self, name, perm='push'):
        raise NotImplementedError

