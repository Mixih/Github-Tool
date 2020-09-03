import argparse
import os

from gitbot.datasources import CSVDataSource
from gitbot.exceptions import AccessDeniedException
from gitbot.gh_org import GHOrg


def process_users(token, organization, filename, colname, interactive=False,
                  team=""):
    try:
        ds = CSVDataSource(filename)
        org = GHOrg(token, organization)
        print("Loading user data from Github API (this might take a while)...",
              end='', flush=True)
        org.update_from_api()
    except AccessDeniedException:
        print('\nAn access error occured during initialization. Check the'
              ' access right of the token')
        return
    print("DONE")
    new_members = []
    new_team_members = []
    new_repos = []

    for user in ds.get_users(colname):
        if not org.check_member(user):
            if org.check_valid_user(user):
                new_members.append(user)
            else:
                print("Invalid user {}".format(user))
                continue
        if team:
            try:
                if not org.check_team(user, team):
                    new_team_members.append(user)
            except KeyError:
                return
        if not org.check_repo(user):
            new_repos.append(user)

    if interactive:
        print("Planning to invite users:")
        for user in new_members:
            print(user)
        print("==========================")
        print("Planning to add user to team {}".format(team))
        for user in new_team_members:
            print(user)
        print("==========================")
        print("Planning to create user repos for:")
        for repo in new_repos:
            print(repo)
        print("Continue?(y/n) ", end='')
        conf = input()
        if conf != 'y':
            print('aborting sync')
            return

    for user in new_members:
        print('Inviting user {}'.format(user))
        org.add_member(user)

    for user in new_team_members:
        print('Adding user {} to team {}'.format(user, team))
        org.add_member_to_team(user, team)

    for repo in new_repos:
        print('Adding user repo {}'.format(repo))
        org.add_private_repo(repo)
        # here the user has the same name as their repo
        org.add_user_to_repo(repo, repo)


def main():
    parser = argparse.ArgumentParser(description="Hosted git repository sync"
                                                 "for personal repositories as"
                                                 "part of an org")
    parser.add_argument('datasource', help='datasource to sync from')
    parser.add_argument('org', help='organization to sync users with')
    parser.add_argument('--team', default='', help='team to check users'
                        'against')
    parser.add_argument('--git-token', '-t', default='',
                        help='token to use to authenticate again the hosted git'
                             'provider. Pass a environment variable to prevent'
                             'leaving the api-key in shell history')
    parser.add_argument('--col-name', '-c', default='username',
                        help='Name of colume to use as the usernames from the '
                             'datasource')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Confirm modification before applying them')
    args = parser.parse_args()

    git_token = args.git_token
    if git_token and git_token[0] == '$':
        token = os.environ.get(git_token[1:])
        if token is not None:
            git_token = token

    process_users(git_token, args.org, args.datasource, args.col_name,
                  args.interactive, args.team)


if __name__ == '__main__':
    main()
