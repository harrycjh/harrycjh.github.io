# 法兰城运维与发布说明（v4.41）

> 适用版本：`v4.41`

## 1. 当前版本号需要同步的地方

发布新版本时，至少要同步以下位置：

- 根目录版本文件：[/Users/chujianhe/.openclaw/workspace-taizi/VERSION](/Users/chujianhe/.openclaw/workspace-taizi/VERSION)
- 页面版本与标题：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2) [/Users/chujianhe/.openclaw/workspace-taizi/index.html#L9](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L9)
- 页面内构建常量：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3444](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3444)
- PWA manifest 版本：[/Users/chujianhe/.openclaw/workspace-taizi/manifest.webmanifest#L2](/Users/chujianhe/.openclaw/workspace-taizi/manifest.webmanifest#L2)
- `sw.js` 注册 query 参数：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3519](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3519)
- `sw.js` 缓存命名：[/Users/chujianhe/.openclaw/workspace-taizi/sw.js#L1](/Users/chujianhe/.openclaw/workspace-taizi/sw.js#L1)

## 2. 版本与缓存的关系

当前缓存分两层：

1. `FALAN_BUILD_VERSION`
   - 用来判断是否需要清浏览器缓存与重新注册 SW
2. `sw.js` 里的 cache namespace
   - `SHELL_CACHE`
   - `RUNTIME_CACHE`

两者都要同步考虑，不能只改其一。

## 3. 强制清缓存方式

当前页面支持：

- `?falan_nocache=1`
- `?cache=clear`

行为：

- 清空 `Cache Storage`
- 注销 `service worker`
- 重写本地版本号
- 再刷新页面

相关代码：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3447](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3447)

## 4. Service Worker 说明

当前 `sw.js` 负责：

- 预缓存首页、manifest、PWA 图标
- 预缓存 object-map 关键资源
- 运行时请求优先走缓存，再回源

文件：[/Users/chujianhe/.openclaw/workspace-taizi/sw.js](/Users/chujianhe/.openclaw/workspace-taizi/sw.js)

## 5. 本地启动

不要直接用 `file://` 打开。

当前仓库已经自带本地启动脚本：

- Windows bat：[/Users/chujianhe/.openclaw/workspace-taizi/start-local-server.bat](/Users/chujianhe/.openclaw/workspace-taizi/start-local-server.bat)
- Windows PowerShell：[/Users/chujianhe/.openclaw/workspace-taizi/start-local-server.ps1](/Users/chujianhe/.openclaw/workspace-taizi/start-local-server.ps1)

默认端口：

- `http://127.0.0.1:8765/`

如果在 macOS / Linux 手动起服务，也建议使用静态 HTTP 服务，而不是 `file://`。

## 6. 线上发布

当前项目发布到 GitHub Pages，仓库是：

- [https://github.com/harrycjh/harrycjh.github.io](https://github.com/harrycjh/harrycjh.github.io)

常规发布动作：

1. 同步版本号
2. 提交本地 git
3. 推送 `main`
4. 如遇旧缓存，使用 `?falan_nocache=1`

## 7. 页面里有哪些调试工具

当前页面右侧/移动端 HUD 有这些调试入口：

- 选人界面
- 全屏游玩
- 音乐开关
- 障碍格开关
- 帧耗时开关
- 5 倍移速
- 调试传送

DOM 入口：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L952](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L952)

## 8. 页面启动顺序

`bootstrapFalan()` 当前会做：

1. 检查并清理旧缓存
2. 同步相机/UI/选人状态
3. 注册 `service worker`
4. 启动物件地图加载
5. 如是移动端，补横屏和沉浸处理
6. 启动主循环

入口：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3543](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3543)

## 9. 文档维护规则

以下情况必须同步更新文档：

- 版本号同步策略变化
- 本地启动端口或脚本变化
- `sw.js` 预缓存列表变化
- object-map 主资源变化
- 调试工具面板变化
- 发布方式变化
