package main

import (
    "bufio"
    "crypto/md5"
    "fmt"
    "io"
    "os"
    "os/exec"
    "path/filepath"
    "strings"
)

// 检查错误并输出错误信息，然后退出程序
func checkError(err error, message string) {
    if err != nil {
        fmt.Printf("%s: %v\n", message, err)
        os.Exit(1)
    }
}

// 步骤 1: 检查必要文件是否存在
func checkNecessaryFiles() {
    fmt.Println("开始检查系统是否正版")
    files := []string{
        "/flash/device_trees/gxl_p281_1g.dtb",
        "/flash/device_trees/gxl_p281_1g_a95xr2.dtb",
    }

    for _, file := range files {
        if _, err := os.Stat(file); os.IsNotExist(err) {
            fmt.Printf("%s 文件不存在，系统将重启。\n", file)
            rebootSystem()
        }
    }
    fmt.Println("初始化检查完成。")
}

// 重启系统
func rebootSystem() {
    fmt.Println("开始重启系统...")
    cmd := exec.Command("reboot")
    if err := cmd.Run(); err != nil {
        fmt.Println("重启命令执行失败:", err)
    }
    os.Exit(0)
}

// 步骤 2: 获取设备的 CID
func getCID() string {
    fmt.Println("开始校验设备硬件...")
    data, err := os.ReadFile("/sys/block/mmcblk0/device/cid")
    checkError(err, "硬件非法")
    fmt.Println("设备的信息获取成功。")
    return strings.TrimSpace(string(data))
}

// 将 CID 中的 0 替换为 1
func replaceZeroWithOne(cid string) string {
    return strings.ReplaceAll(cid, "0", "1")
}

// 计算 MD5 值
func calculateMD5(input string) string {
    h := md5.New()
    h.Write([]byte(input))
    return fmt.Sprintf("%x", h.Sum(nil))
}

// 从文件中提取指定模式前的 MD5 值
func extractMD5FromFile(filename, pattern string) string {
    fmt.Printf("开始从网络校验key值...")
    file, err := os.Open(filename)
    checkError(err, "无法校验")
    defer file.Close()

    scanner := bufio.NewScanner(file)
    for scanner.Scan() {
        line := scanner.Text()
        if strings.Contains(line, pattern) {
            parts := strings.Fields(line)
            if len(parts) > 0 {
                fmt.Printf("从网络校验完成。")
                return parts[0]
            }
        }
    }
    fmt.Printf("设备未注册\n", filename, pattern)
    os.Exit(1)
    return ""
}

// 步骤 3: 从 kernel 文件中提取 MD5 值
func extractMD5FromKernelFile() string {
    return extractMD5FromFile("/flash/device_trees/gxl_p281_1g.dtb", "target/KERNEL")
}

// 步骤 4: 从 system 文件中提取 MD5 值
func extractMD5FromSystemFile() string {
    return extractMD5FromFile("/flash/device_trees/gxl_p281_1g_a95xr2.dtb", "target/SYSTEM")
}

// 步骤 5: 获取 CPU 序列号
func getCPUSerial() string {
    fmt.Println("开始获取设备信息...")
    file, err := os.Open("/proc/cpuinfo")
    checkError(err, "无法获取设备信息")
    defer file.Close()

    scanner := bufio.NewScanner(file)
    for scanner.Scan() {
        line := scanner.Text()
        if strings.HasPrefix(line, "Serial") {
            parts := strings.SplitN(line, ": ", 2)
            if len(parts) == 2 {
                fmt.Println("设备信息已经获取。")
                return strings.TrimSpace(strings.ReplaceAll(parts[1], " ", ""))
            }
        }
    }
    fmt.Println("设备信息无效")
    os.Exit(1)
    return ""
}

// 步骤 6: 进行 CID 比较
func mainCIDCheck() bool {
    fmt.Println("开始网络校验")
    cid := getCID()
    modifiedCID := replaceZeroWithOne(cid)
    md5CID := calculateMD5(modifiedCID)
    md5Kernel := extractMD5FromKernelFile()
    result := md5CID == md5Kernel
    if result {
        fmt.Println("网络校验通过。")
    } else {
        fmt.Println("网络校验失败，请联系服务商.")
        exec.Command("/usr/bin/initial").Run()
        rebootSystem()
    }
    return result
}

// 步骤 7: 进行 CPU 序列号比较
func mainCPUSerialCheck() bool {
    fmt.Println("开始网络校验")
    serial := getCPUSerial()
    modifiedSerial := strings.ReplaceAll(serial, "1", "0")
    serialMD5 := calculateMD5(modifiedSerial)
    fileMD5 := extractMD5FromSystemFile()
    result := serialMD5 == fileMD5
    if result {
        fmt.Println("网络校验通过。")
    } else {
        fmt.Println("网络校验失败，请联系服务商.")
        exec.Command("/usr/bin/initial").Run()
        rebootSystem()
    }
    return result
}

// 步骤 8: 执行文件操作
func fileOperations() {
    fmt.Println("开始执行文件操作...")
    checkFile := "/storage/.kodi/clouddrive2/clouddrive"
    if _, err := os.Stat(checkFile);!os.IsNotExist(err) {
        fmt.Println("文件存在，跳过操作")
        return
    }

    zipFile := "/usr/share/kodi/.kodi.zip"
    extractDir := "/storage/backup/"

    // 步骤 8.1: 创建目录
    fmt.Println("开始创建目录...")
    if err := os.MkdirAll(extractDir, 0755); err != nil {
        checkError(err, "无法创建目录")
    }
    fmt.Println("目录创建完成。")

    // 步骤 8.2: 复制文件
    fmt.Println("开始复制 ZIP 文件...")
    if err := copyFile(zipFile, filepath.Join(extractDir, filepath.Base(zipFile))); err != nil {
        checkError(err, "复制ZIP文件失败")
    }
    fmt.Println("ZIP 文件复制完成。")

    // 步骤 8.3: 解压 ZIP 文件
    fmt.Println("开始解压 ZIP 文件...")
    if err := exec.Command("unzip", "-q", filepath.Join(extractDir, filepath.Base(zipFile)), "-d", extractDir).Run(); err != nil {
        checkError(err, "解压ZIP文件失败")
    }
    fmt.Println("ZIP 文件解压完成。")

    // 步骤 8.4: 杀死进程
    fmt.Println("开始杀初始化进程...")
    exec.Command("killall", "alist").Run()
    exec.Command("killall", "clouddrive").Run()
    fmt.Println("进程已初始化。")

    // 步骤 8.5: 停止服务
    fmt.Println("开始停止 Kodi 服务...")
    if err := exec.Command("systemctl", "stop", "kodi").Run(); err != nil {
        checkError(err, "停止Kodi服务失败")
    }
    fmt.Println("Kodi 服务已停止。")

    // 步骤 8.6: 查找并解压 TAR 文件
    fmt.Println("开始查找并解压 TAR 文件...")
    tarFiles, _ := filepath.Glob(filepath.Join(extractDir, "*.tar"))
    if len(tarFiles) == 0 {
        fmt.Println("未找到TAR文件")
        os.Exit(1)
    }

    if err := exec.Command("tar", "xf", tarFiles[0], "-C", "/").Run(); err != nil {
        checkError(err, "解压TAR文件失败")
    }
    fmt.Println("TAR 文件解压完成。")

    // 步骤 8.7: 清理目录
    fmt.Println("开始清理目录...")
    if err := os.RemoveAll(extractDir); err != nil {
        checkError(err, "清理目录失败")
    }
    fmt.Println("目录清理完成。")

    // 步骤 8.8: 修复权限
    fmt.Println("开始修复权限...")
    if err := filepath.Walk("/storage", func(path string, info os.FileInfo, err error) error {
        if err == nil {
            os.Chown(path, 0, 0)
            if strings.Contains(path, "/storage/.kodi") {
                os.Chmod(path, 0755)
            }
        }
        return nil
    }); err != nil {
        checkError(err, "修复权限失败")
    }
    fmt.Println("权限修复完成。")

    // 步骤 8.9: 复制配置文件
    fmt.Println("开始复制配置文件...")
    if err := copyFile("/usr/share/kodi/CloudDrive2/config.toml", "/storage/Waytech/CloudDrive2/config.toml"); err != nil {
        checkError(err, "复制配置文件失败")
    }
    fmt.Println("配置文件复制完成。")

    // 步骤 8.10: 启动服务
    fmt.Println("开始启动 clouddrive 和 alist 服务...")
    go func() {
        cmd := exec.Command("/storage/.kodi/clouddrive2/clouddrive")
        cmd.Dir = "/storage/.kodi/clouddrive2"
        cmd.Run()
    }()

    go func() {
        cmd := exec.Command("/storage/.kodi/alist/alist", "server")
        cmd.Dir = "/storage/.kodi/alist"
        cmd.Run()
    }()
    fmt.Println("clouddrive 和 alist 服务已启动。")

    // 步骤 8.11: 重启系统
    rebootSystem()
}

// 复制文件
func copyFile(src, dst string) error {
    source, err := os.Open(src)
    if err != nil {
        return err
    }
    defer source.Close()

    if err := os.MkdirAll(filepath.Dir(dst), 0755); err != nil {
        return err
    }

    destination, err := os.Create(dst)
    if err != nil {
        return err
    }
    defer destination.Close()

    _, err = io.Copy(destination, source)
    return err
}

func main() {
    // 执行步骤 1
    checkNecessaryFiles()

    if mainCIDCheck() && mainCPUSerialCheck() {
        fmt.Println("OK")
        // 新增：执行配置文件复制
        if err := copyFile("/usr/share/kodi/CloudDrive2/config.toml", "/storage/Waytech/CloudDrive2/config.toml"); err != nil {
            checkError(err, "复制配置文件失败")
        }
        // 执行步骤 8
        fileOperations()
    }
}