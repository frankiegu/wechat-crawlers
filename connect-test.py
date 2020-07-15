'''
连接测试

确保当前只连接了一台设备，否则请指定
要连接的设备名，如u2.connect('8deb4459')
设备名通过 adb devices 查看
测试结果形如：
{'currentPackageName': 'com.tencent.mm', 'displayHeight': 1920, 'displayRotation': 0,
'displaySizeDpX': 360,'displaySizeDpY': 640, 'displayWidth': 1080, 'productName': 'sagit',
'screenOn': True, 'sdkInt': 28, 'naturalOrientation': True}
'''


import uiautomator2 as u2

d = u2.connect() # connect to device
print(d.info)
