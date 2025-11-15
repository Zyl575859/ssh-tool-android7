# 📤 上传代码到GitHub - 详细操作步骤

## 🎯 目标
将本地代码上传到GitHub，然后使用GitHub Actions自动构建APK

---

## 📋 步骤1：安装Git（如果还没有）

### 检查是否已安装Git

1. **打开命令提示符或PowerShell**
   - 按 `Win + R`
   - 输入 `cmd` 或 `powershell`
   - 按回车

2. **检查Git**
   ```bash
   git --version
   ```

3. **如果显示版本号**（如 `git version 2.40.0`）
   - ✅ 已安装，跳到步骤2

4. **如果显示"不是内部或外部命令"**
   - ❌ 需要安装Git
   - 下载：https://git-scm.com/download/win
   - 安装时全部选择默认选项即可

---

## 📋 步骤2：创建GitHub账号（如果还没有）

1. **访问GitHub**
   - 打开：https://github.com
   - 点击右上角 "Sign up"（注册）

2. **填写信息**
   - 用户名（Username）
   - 邮箱（Email）
   - 密码（Password）

3. **验证邮箱**
   - 检查邮箱，点击验证链接

---

## 📋 步骤3：在GitHub上创建新仓库

1. **登录GitHub后**
   - 点击右上角 `+` 号
   - 选择 "New repository"（新建仓库）

2. **填写仓库信息**
   - **Repository name**（仓库名）：例如 `ssh-tool-android`
   - **Description**（描述）：可选，例如 "SSH工具Android版本"
   - **Public**（公开）或 **Private**（私有）：选择Public（免费）
   - **不要勾选** "Add a README file"（我们本地已有代码）
   - **不要勾选** "Add .gitignore" 和 "Choose a license"

3. **点击 "Create repository"（创建仓库）**

4. **记住仓库地址**
   - 会显示类似：`https://github.com/你的用户名/ssh-tool-android.git`
   - 复制这个地址，后面会用到

---

## 📋 步骤4：在本地初始化Git并上传代码

### 方法A：使用命令提示符/PowerShell（推荐）

1. **打开命令提示符或PowerShell**
   - 按 `Win + R`
   - 输入 `cmd` 或 `powershell`
   - 按回车

2. **进入项目目录**
   ```bash
   cd C:\Users\Lenovo\Desktop\999999999
   ```

3. **初始化Git仓库**
   ```bash
   git init
   ```
   - 会显示：`Initialized empty Git repository in ...`

4. **添加所有文件**
   ```bash
   git add .
   ```
   - 这会添加当前目录下的所有文件

5. **创建第一次提交**
   ```bash
   git commit -m "初始提交"
   ```
   - 如果是第一次使用Git，可能需要配置用户名和邮箱：
   ```bash
   git config --global user.name "你的名字"
   git config --global user.email "你的邮箱"
   ```
   - 然后重新执行 `git commit -m "初始提交"`

6. **添加远程仓库地址**
   ```bash
   git remote add origin https://github.com/你的用户名/你的仓库名.git
   ```
   - **替换** `你的用户名` 为你的GitHub用户名
   - **替换** `你的仓库名` 为你在步骤3创建的仓库名
   - 例如：`git remote add origin https://github.com/zhangsan/ssh-tool-android.git`

7. **上传代码到GitHub**
   ```bash
   git push -u origin main
   ```
   - 如果是第一次，会弹出登录窗口
   - 输入GitHub用户名和密码（或使用Personal Access Token）

### 方法B：使用GitHub Desktop（图形界面，更简单）

1. **下载GitHub Desktop**
   - 访问：https://desktop.github.com
   - 下载并安装

2. **登录GitHub账号**
   - 打开GitHub Desktop
   - 登录你的GitHub账号

3. **添加本地仓库**
   - 点击 "File" → "Add Local Repository"
   - 选择项目目录：`C:\Users\Lenovo\Desktop\999999999`
   - 点击 "Add repository"

4. **提交代码**
   - 在左侧会显示所有更改的文件
   - 在底部输入提交信息：`初始提交`
   - 点击 "Commit to main"

5. **发布到GitHub**
   - 点击 "Publish repository"
   - 输入仓库名（例如：`ssh-tool-android`）
   - 选择 Public
   - 点击 "Publish repository"

---

## 📋 步骤5：触发自动构建

### 自动触发（推荐）

代码上传后，GitHub Actions会自动开始构建：
1. 进入你的GitHub仓库页面
2. 点击 "Actions" 标签
3. 会看到 "构建Android APK" 工作流正在运行
4. 点击进入查看构建进度

### 手动触发

1. 进入GitHub仓库
2. 点击 "Actions" 标签
3. 在左侧选择 "构建Android APK"
4. 点击右侧 "Run workflow" 按钮
5. 选择分支（通常是 `main`）
6. 点击绿色的 "Run workflow" 确认

---

## 📋 步骤6：下载APK

1. **等待构建完成**（约10-20分钟）
   - 在 "Actions" 页面可以看到构建进度
   - 绿色勾号表示成功

2. **下载APK**
   - 点击完成的构建记录
   - 滚动到页面底部 "Artifacts" 部分
   - 点击 "android-apk" 下载
   - 解压后会看到APK文件

---

## ❓ 常见问题

### Q: Git push时提示需要认证？
A: 
1. 使用Personal Access Token（推荐）
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - 点击 "Generate new token"
   - 勾选 `repo` 权限
   - 复制生成的token
   - push时密码处输入这个token

2. 或使用GitHub Desktop（更简单）

### Q: 提示"remote origin already exists"？
A: 
```bash
git remote remove origin
git remote add origin https://github.com/你的用户名/你的仓库名.git
```

### Q: 如何更新代码？
A: 
```bash
git add .
git commit -m "更新说明"
git push
```

### Q: 构建失败怎么办？
A: 
- 在Actions页面查看错误日志
- 通常是依赖问题，可以修改 `.github/workflows/build_apk.yml`

---

## 💡 快速命令参考

```bash
# 进入项目目录
cd C:\Users\Lenovo\Desktop\999999999

# 初始化Git
git init

# 添加文件
git add .

# 提交
git commit -m "初始提交"

# 添加远程仓库（替换为你的地址）
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 上传
git push -u origin main
```

---

## 🎉 完成！

上传成功后，GitHub Actions会自动开始构建APK，你只需要等待并下载即可！

