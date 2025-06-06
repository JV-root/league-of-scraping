xpath_options_dict = {
    'game_time': list(([
    '/html/body/div/main/div[2]/div/div[3]/div/div/div/div[1]/div/div/div[1]/div[2]/h1'
])),
    'game_date': list(([
        '/html/body/div/main/div[2]/div/div[1]/div[2]'

])),

    'team_gold_blue_side': list(([
        "//span[contains(@class, 'score-box') and contains(@class, 'blue_line') and .//img[contains(@alt, 'Gold')]]"
    ])),
    'team_gold_red_side': list(([
        "//span[contains(@class, 'score-box') and contains(@class, 'red_line') and .//img[contains(@alt, 'Gold')]]"
    ])),
    'team_blue_kills': list(([
        "//span[contains(@class, 'score-box') and contains(@class, 'blue_line') and .//img[contains(@alt, 'Kills')]]"
    ])),
    'team_red_kills': list(([
    "//span[contains(@class, 'score-box') and contains(@class, 'red_line') and .//img[contains(@alt, 'Kills')]]"
    ])),


}