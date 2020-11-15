### TO SETUP KEYBASE & systemctl ON BISQ MONITOR SERVER:

**reference material:**

- https://support.nine.ch/articles/manage-daemons-as-user-with-systemd
- https://support.nine.ch/articles/user-systemd-unit-files

**as root:**

    useradd -m tmpmonitorbot45
    passwd tmpmonitorbot45
    usermod -aG sudo tmpmonitorbot45
    
   -> `vi /etc/passwd` change default shell to `/bin/bash`
 
**as tmpmonitorbot45:**

    download keybase_amd64.deb
    sudo apt install ./keybase_amd64.deb
    run_keybase -g
    keybase oneshot --paperkey "remove remove remove remove remove remove remove remove remove remove remove remove remove" --username tmpmonitorbot45
    keybase whoami
    keybase chat send jmacxx "testing keybase message from server"


**create user-level processes for alerting keybase and serving the web app:**

    cd ~/.config
    mkdir systemd
    cd systemd
    mkdir user
    cd user

    cat > bisq-alerts.service <<EOF
    [Unit]
    Description=bisq-alerts
    After=multi-user.target
    [Service]
    WorkingDirectory=/home/tmpmonitorbot45
    ExecStart=python3 -u ./bisq-alerts.py
    Type=idle
    StandardOutput=syslog
    StandardError=syslog
    SyslogIdentifier=bisq-alerts
    [Install]
    WantedBy=default.target
    EOF
  
    cat > bisq-monitor-app.service <<EOF
    [Unit]
    Description=bisq-monitor-app
    After=multi-user.target
    [Service]
    WorkingDirectory=/home/tmpmonitorbot45
    ExecStart=python3 -u ./bisq-monitor-app.py
    Type=idle
    StandardOutput=syslog
    StandardError=syslog
    SyslogIdentifier=bisq-monitor-app
    [Install]
    WantedBy=default.target
    EOF
      
**enable and start the two python processes:**

    systemctl --user enable bisq-monitor-app.service
    systemctl --user enable bisq-alerts.service
    systemctl --user restart bisq-monitor-app.service
    systemctl --user restart bisq-alerts.service
    systemctl --user status bisq-monitor-app.service
    systemctl --user status bisq-alerts.service

**to watch the service log files**

    journalctl --user-unit=bisq-alerts.service --user-unit=bisq-monitor-app.service -f



