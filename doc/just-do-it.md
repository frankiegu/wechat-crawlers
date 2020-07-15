# 环境搭建不完全指北

## Windows + Android 真机篇

### [uiautomator2](https://github.com/openatx/uiautomator2)
- Android版本 4.4+
- Python 3.6+ (社区反馈3.8.0不支持, 但是3.8.2支持）
- JAVA 1.8+
- Android SDK

```
# 确保手机已连接
adb devices 
# 安装uiautomator2
pip3 install -U uiautomator2
# 安装包含httprpc服务的apk到手机
python3 -m uiautomator2 init
```
正常执行完之后，手机上会多一个**ATX**的应用。

可以通过执行`uiautomator2 --help`检查是否安装成功,或执行**connect-test.py**文件。    
![connect-test.png](https://cdn.jsdelivr.net/gh/hu-qi/wechat-crawlers/example/connect-test.png)

然后执行`pip3 install -U  weditor`安装**[weditor](https://github.com/openatx/weditor)**,以便查看应用的UI。
通过执行`weditor -h`检查是否安装成，执行`weditor`可启动。
启动**weditor**默认打开**http://localhost:17310/**，我们可以选取**Android**平台，输入连接的设备ID（通过`adb devices`获取）,选择**Connect**再点击**Dump Hierarchy**刷新即可。    
![weditor.png](https://cdn.jsdelivr.net/gh/hu-qi/wechat-crawlers/example/weditor.png)