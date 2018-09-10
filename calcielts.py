#! /usr/bin/env python3
#! -*- coding:utf-8 -*-

import bs4
import requests
import os
import json
import matplotlib.pyplot as plt
import datetime

def statperson(url):
    commits = dict()
    resp = requests.get(url)
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    partialurl = soup.find('li', class_="commits").find("a")['href']
    nextpage = "https://www.github.com" + partialurl
    while True:
        print("Checking commited page %s ... " % (nextpage))
        soup = bs4.BeautifulSoup(requests.get(nextpage).text, "html.parser")
        boards = soup.find("div", class_ = "commits-listing commits-listing-padded js-navigation-container js-active-navigation-container")
        board_titles = boards.find_all("div", class_ = "commit-group-title")
        for board_title in board_titles:
            date = board_title.text.strip().replace("Commits on", "").strip()
            if(date not in commits.keys()): commits[date] = 0
            commit_record = board_title.find_next_sibling().find_all("li")
            commits[date] += len(commit_record)
        sentry = soup.find("div", class_ = "pagination").find("span")
        if sentry: sentry = sentry.text.strip()
        if sentry == "Older": break
        pagelinks = soup.find("div", class_ = "pagination").find_all("a")
        nextpage = pagelinks[len(pagelinks) - 1]["href"]
    return commits

if __name__ == "__main__":

    users = {"w.liu":"https://github.com/lw19960617/IELTS",
            "h.chen":"https://github.com/yiyijoyce/IELTS",
            "my.wen":"https://github.com/wenmeiyu/ielts",
            "dd.che":"https://github.com/ddche/IELTS",
            "zq.li":"https://github.com/ikey4u/ielts" }

    datafile = "userstat.json"
    data = dict()

    if not os.path.exists(datafile):
        for user in users.keys():
            print("[+] Processing user %s ..." % (user))
            data[user] = statperson(users[user])
        with open(datafile, "w") as _:
            json.dump(data, _)
        print("[OK] Data file has been saved to %s!" % (datafile))
    else:
        with open(datafile, "r") as _:
            data = json.load(_)

    startdate = datetime.datetime.strptime("2018-07-05", "%Y-%m-%d")
    enddate = datetime.datetime.strptime("2018-09-05", "%Y-%m-%d")
    curdate = startdate
    fig, axes = plt.subplots(nrows = len(data.keys()) + 1, ncols = 1, figsize=(8.27, 11.69))
    userid = 0
    usernum = len(data.keys())
    stat = dict()
    for user in data.keys():
        curdate = startdate
        print("[+] Read the data of user %s ..." % (user))
        pltdata = dict()
        pltdata['day'] = list()
        pltdata['count'] = list()
        pltdata['offday'] = list()
        pltdata['absence'] = 0
        pltdata['failure'] = 0
        while curdate <= enddate:
            readable_key = curdate.strftime("%Y-%m-%d")
            pltdata['offday'].append((curdate - startdate).days)
            pltdata['day'].append(readable_key)

            count = 0
            daykey = curdate.strftime("%b %-d, %Y")
            if daykey in data[user].keys():
                count = data[user][daykey]
                if count < 3: pltdata['failure'] += 1
            else:
                pltdata['absence'] += 1
            pltdata['count'].append(count)
            curdate += datetime.timedelta(days = 1)

        total = (enddate - startdate).days + 1
        absence = pltdata['absence']
        failure = pltdata['failure']
        rate = (total - absence - failure) / total
        stat[user] = [total, absence, failure, "%.2f" % (rate)]
        axes[userid].plot(pltdata['offday'], pltdata['count'])
        axes[userid].set_title(user)
        axes[userid].set_xticks(pltdata['offday'][0::2])
        axes[userid].set_yticks(range(0, 8, 2))
        axes[userid].set_xlabel("The nth day")
        axes[userid].set_ylabel("Count")
        userid += 1

    userlist = []
    userstat = []
    for user in stat.keys():
        userlist.append(user)
        userstat.append(stat[user])
    axes[userid].set_xticks([])
    axes[userid].set_yticks([])
    axes[userid].axis('off')
    collabels = ['total', 'absence', 'failure', 'rate(%)']
    table = plt.table(cellText = userstat,
            colWidths = [0.2] * len(collabels),
            cellLoc = 'center',
            rowLabels = userlist,
            colLabels = collabels,
            fontsize = 5,
            loc = 'best')
    table.scale(1.1, 4)
    axes[userid].table = table
    plt.subplots_adjust(hspace = 3)
    plt.savefig("stat.pdf")
    #  plt.show()

