def add_variables(xpath_variables: dict) -> None:
    xpath_variables['market_purchase'] = {}
    xpath_variables['market_purchase']['accept_ssa'] = '//*[@id="market_buynow_dialog_accept_ssa"]'
    xpath_variables['market_purchase']['btn_buy'] = '//*[@id="market_buynow_dialog_purchase"]'
    xpath_variables['market_purchase']['dialog_close'] = '//*[@id="market_buynow_dialog_close"]'