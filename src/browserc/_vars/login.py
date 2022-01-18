def add_variables(xpath_variables: dict) -> None:
    xpath_variables['login'] = {}
    xpath_variables['login']['input_username'] = '//*[@id="input_username"]'
    xpath_variables['login']['input_password'] = '//*[@id="input_password"]'
    xpath_variables['login']['signin_button'] = '//*[@id="login_btn_signin"]/button'

    xpath_variables['login']['twofactorcode_input'] = '//*[@id="twofactorcode_entry"]'
    xpath_variables['login']['twofactorcode_code'] = '//*[@id="login_twofactorauth_buttonset_entercode"]/div[1]'