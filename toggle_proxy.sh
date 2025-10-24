#!/bin/bash
srv="Wi-Fi"; host=127.0.0.1; port=8080
if [[ "$1" == "on" ]]; then
    sudo networksetup -setwebproxy "$srv" "$host" "$port"
    sudo networksetup -setsecurewebproxy "$srv" "$host" "$port"
    echo "全局代理已开启 → $host:$port"
else
    sudo networksetup -setwebproxystate "$srv" off
    sudo networksetup -setsecurewebproxystate "$srv" off
    echo "全局代理已关闭"
fi