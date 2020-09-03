import argparse
import os

from gitbot.datasources import CSVDataSource
from gitbot.exceptions import AccessDeniedException
from gitbot.gh_org import GHOrg


def process_users(token, organization, filename, usercol, namecol, namefmt,
                  interactive=False, team=""):
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

    try:
        for (user, r_name) in ds.get_users(usercol, namecol):
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
            repo_name = namefmt.format(r_name)
            if not org.check_repo(user):
                new_repos.append((repo_name, user))
    except KeyError:
        print('An invalid column was specified. Please check the spelling of '
              'your column names and try again')
        return

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
        for repo_info in new_repos:
            print(repo_info[0])
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

    for repo_info in new_repos:
        print('Adding user repo {}'.format(repo_info[0]))
        org.add_private_repo(repo_info[0])
        # here the user has the same name as their repo
        org.add_user_to_repo(repo_info[0], repo_info[1])


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
    parser.add_argument('--user-col', '-u', default='username',
                        help='Name of column to use as the usernames from the '
                             'datasource, default is "username"')
    parser.add_argument('--name-col', '-n', default='username',
                        help='Name of column to use as the repo names from the '
                             'datasource, default is "username"')
    parser.add_argument('--name-fmt', default='{}',
                        help='Standard python formatable string with exactly '
                             'one field to fill in the variable aprt of the '
                             'repository names (defualt is "{}")')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Confirm modification before applying them')
    args = parser.parse_args()

    git_token = args.git_token
    if git_token and git_token[0] == '$':
        token = os.environ.get(git_token[1:])
        if token is not None:
            git_token = token

    process_users(git_token, args.org, args.datasource, args.user_col,
                  args.name_col, args.name_fmt, args.interactive, args.team)


if __name__ == '__main__':
    main()
