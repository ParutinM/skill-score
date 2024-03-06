from skill_score.app import App

if __name__ == "__main__":
    app = App.from_toml()
    app.run()

    # show_pages([Page(path=p.value, name=p.name) for p in PagePath])
    #
    # # some sleep
    # sleep(0.1)
    #
    # # SQLAlchemy engine
    # engine = get_engine()
    #
    # # creating cookie manager
    # cookie_manager = get_cookie_manager()
    #
    # # switch page if authorized
    # if is_auth(engine, cookie_manager):
    #     switch_page(PagePath.home.name)
    # else:
    #     switch_page(PagePath.main.name)
