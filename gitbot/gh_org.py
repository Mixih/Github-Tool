from functools import wraps

from github import Github
from github.GithubException import (BadCredentialsException,
                                    UnknownObjectException)

from gitbot.basetypes import RepoOrgBase
from gitbot.exceptions import AccessDeniedException


def catchAccessDenied(func):
    '''
    Decorator to simplify catching an access violation
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except BadCredentialsException:
            print("Access denied for requested operation")
            raise AccessDeniedException
    return wrapper


class GHOrg(RepoOrgBase):

    @catchAccessDenied
    def __init__(self, access_token, org):
        self.github = Github(access_token)
        self.org = self.github.get_organization(org)
        self.members = {}
        self.repos = {}
        self.teams = {}
        self.team_members = {}

    def update_from_api(self):
        self.collect_members()
        self.collect_repos()
        self.collect_teams()

    @catchAccessDenied
    def collect_members(self, team=None):
        if team is not None:
            for user in self.org.get_team(team).get_members():
                self.members[user.login] = user
        else:
            for user in self.org.get_members():
                self.members[user.login] = user

    @catchAccessDenied
    def collect_repos(self):
        for repo in self.org.get_repos():
            self.repos[repo.name] = repo

    @catchAccessDenied
    def collect_teams(self):
        for team in self.org.get_teams():
            self.teams[team.name] = team
            self.team_members[team.name] = set()
            for user in team.get_members():
                self.team_members[team.name].add(user.login)

    def check_member(self, username):
        if username in self.members.keys():
            return True
        else:
            return False

    def check_valid_user(self, username):
        try:
            user = self.github.get_user(username)
        except UnknownObjectException:
            return False
        return True

    def check_team(self, username, team):
        try:
            if username in self.team_members[team]:
                return True
            else:
                return False
        except KeyError:
            print('invalid team "{}"'.format(team))
            raise KeyError

    def check_repo(self, reponame):
        if reponame in self.repos.keys():
            return True
        else:
            return False

    @catchAccessDenied
    def add_member(self, username, role='member', team=None):
        if username in self.members.keys():
            return
        try:
            user = self.github.get_user(username)
        except UnknownObjectException:
            print("can't add invalid user {}".format(username))
            return False

        self.org.add_to_members(user, role)
        self.members[user.login] = user
        if team is not None:
            self.add_member_to_team(username, team, role)
        return True

    @catchAccessDenied
    def add_member_to_team(self, username, team, role='member'):
        if username in self.team_members[team]:
            return
        self.teams[team].add_membership(self.members[username], role)

    @catchAccessDenied
    def add_private_repo(self, name):
        self.org.create_repo(name, private=True)

    @catchAccessDenied
    def add_user_to_repo(self, name, username, perm='push'):
        self.org.get_repo(name).add_to_collaborators(self.members[username],
                                                     perm)

