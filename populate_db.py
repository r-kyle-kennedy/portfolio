from app import add_github_api, app

if __name__ == '__main__':
    with app.app_context():
        add_github_api()
        print('GitHub API sync completed')
