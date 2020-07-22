from ticket.train_ticket.checkticket import CheckTicket
from ticket.train_ticket.buyticket import BuyTicket
import sys
import datetime


def main(date_):
    date_ = datetime.datetime.strptime(date_, '%Y-%m-%d')
    date_ = datetime.datetime.strftime(date_, '%Y-%m-%d')
    print(f'当前日期:{date_}')
    check_ticket = CheckTicket(date=date_, station_start=station_start, station_end=station_end, purpose=purpose)
    relation = check_ticket.get_info
    if len(relation.items()) == 0:
        print('当前没有您选择的票，请重新选择日期或按其他键退出:\n[p]前一天\n[n]后一天\n[r]重新输入日期')
        next_step = input('请输入:')
        if next_step == 'p':
            prev_date = datetime.datetime.strptime(date_, '%Y-%m-%d') + datetime.timedelta(-1)
            prev_date = datetime.datetime.strftime(prev_date, '%Y-%m-%d')
            main(prev_date)
        elif next_step == 'n':
            next_date = datetime.datetime.strptime(date_, '%Y-%m-%d') + datetime.timedelta(1)
            next_date = datetime.datetime.strftime(next_date, '%Y-%m-%d')
            main(next_date)
        elif next_step == 'r':
            new_date = input('请输入日期:')
            main(new_date)
        else:
            sys.exit()
    print('以上为目前可选的列车信息，请按序号选择，或选择其他日期，按Q键退出\n[p]前一天\n[n]后一天\n[r]重新输入日期\n[q]退出')
    index = input('请输入:')
    if index == 'p':
        prev_date = datetime.datetime.strptime(date_, '%Y-%m-%d') + datetime.timedelta(-1)
        prev_date = datetime.datetime.strftime(prev_date, '%Y-%m-%d')
        main(prev_date)
    elif index == 'n':
        next_date = datetime.datetime.strptime(date_, '%Y-%m-%d') + datetime.timedelta(1)
        next_date = datetime.datetime.strftime(next_date, '%Y-%m-%d')
        main(next_date)
    elif index == 'r':
        new_date = input('请输入日期:')
        main(new_date)
    elif index == 'q':
        sys.exit()
    else:
        index = int(index)
    station_abbr = check_ticket.station_abbr()
    username = input("请输入用户名:")
    password = input("请输入用户密码:")
    b = BuyTicket(station_start=station_start, station_end=station_end, date=date_,
                  username=username, password=password, purpose=purpose, attr=station_abbr, num=relation[index])
    b.main()


if __name__ == '__main__':
    station_start = input("请输入始发站:")
    station_end = input("请输入终点站:")
    date_start = input("请输入订票日期(格式:202X-XX-XX):")
    ticket_choose = input("请输入序号[1]成人票  [2]学生票:")
    ticket_choose = int(ticket_choose)
    if ticket_choose == 1:
        purpose = 'ADULT'
    else:
        purpose = '0X00'
    main(date_start)
