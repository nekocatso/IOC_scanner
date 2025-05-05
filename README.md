# Morpheus IOC 扫描器

![Morpheus IOC Scanner Logo](placeholder_for_logo.png) <!-- 请替换为实际的 Logo 图片路径或 URL -->

**在威胁开始前检测和防御**

Morpheus IOC 扫描器是一款尖端解决方案，用于检测和分析恶意文件，包括勒索软件和妥协指标 (IOCs)。Morpheus 融合了定制规则和企业级 YARA 集成，实现全面的文件分析和强大的威胁检测。它专为现代网络安全挑战而设计，帮助您自信地应对新兴威胁。

## 目录

- [Morpheus IOC 扫描器](#morpheus-ioc-扫描器)
  - [目录](#目录)
  - [主要特性](#主要特性)
  - [为什么使用 Morpheus](#为什么使用-morpheus)
  - [项目结构](#项目结构)
  - [工作模式](#工作模式)
    - [1) VirusTotal 扫描 (在线)](#1-virustotal-扫描-在线)
    - [2) 默认扫描 (YARA - 离线)](#2-默认扫描-yara---离线)
  - [安装与更新](#安装与更新)
    - [安装](#安装)
    - [更新 YARA 数据库](#更新-yara-数据库)
  - [常见问题 (FAQ)](#常见问题-faq)
  - [使用示例 (Morpheus V2)](#使用示例-morpheus-v2)

## 主要特性

*   **KRYPT0S 勒索软件定制检测**：包含针对 KRYPT0S 勒索软件 POC 的专门检测。 ([查看项目](link_to_kryptos_project)) <!-- 请替换为 KRYPT0S 项目的实际链接 -->
*   **高质量 YARA 规则**：使用企业级 YARA 规则 (`yara_rules/`) 检测恶意软件，实现彻底可靠的扫描。
*   **文件信息提取**：通过定制规则 (`yara_rules/file_analysis/`) 提取详细的文件相关信息，为全面文件分析而设计。
*   **最新 YARA 规则**：使用 `database_updater.py` 脚本，在 GitHub 存储库更新时立即获取新的 Yara 规则。
*   **VirusTotal 集成**：可选择与 VirusTotal 集成 (`modules/virus_total.py`)，利用多引擎分析深入了解潜在威胁。
*   **跨平台兼容**：确保它可以在 Windows 和 Linux 机器上运行。
*   **高速分析**：使用动态多线程高效加速任何大小文件的扫描，利用其广泛数据库快速检测匹配并优化处理速度。
*   **分析后 PDF 文档**：能够将所有结果编译成 PDF 文档 (`modules/analysis_report.py`)，以便进一步分析和展示。
*   **AI 最终判断**：MORPHEUS_IQ (`modules/ai_verdict.py`) 对文件及其恶意软件分析提供全面判断，基于签名检测和分析结果提供详细反馈和见解。

## 为什么使用 Morpheus

Morpheus 提供一系列强大功能，使其成为恶意软件分析的必备工具：

*   **闪电般的分析速度**：使用动态多线程快速扫描大型文件集，在几秒钟内提供结果，且不影响准确性。
*   **尖端威胁检测**：基于强大的 YARA 规则集，Morpheus 可识别广泛的威胁，从常见恶意软件到高级多阶段攻击。
*   **始终保持最新**：通过无缝 YARA 规则更新，Morpheus 确保其检测能力对最新威胁保持有效。
*   **用户友好界面**：具有直观设计，使其对网络安全领域的经验丰富的专业人员和初学者都易于使用。
*   **全面报告**：生成详细、可操作的报告，支持恶意软件调查并增强事件响应工作流程。

Morpheus 的目标是全面应对攻击生命周期中的各个阶段的威胁，防御如同明天不再来临。

## 项目结构

```
IOC_scanner/
├── Main Files/             # 主要执行文件和模块
│   ├── morpheus_scanner.py # 主扫描程序入口
│   ├── setup.py            # 初始化设置脚本 (下载 YARA 规则等)
│   ├── database_updater.py # YARA 规则更新脚本
│   ├── requirements.txt    # Python 依赖项列表
│   ├── yara_rule_tester.py # (可选) YARA 规则测试工具
│   ├── modules/            # 功能模块
│   │   ├── yara_analysis.py  # YARA 扫描逻辑
│   │   ├── virus_total.py  # VirusTotal API 集成
│   │   ├── pe_analysis.py    # PE 文件分析
│   │   ├── analysis_report.py# PDF 报告生成
│   │   ├── ai_verdict.py     # AI 判断模块
│   │   └── ...             # 其他辅助模块
│   ├── test_data/          # (可选) 用于测试的示例数据
│   └── version_tracking/   # (可选) 版本信息
├── yara_rules/             # YARA 规则库
│   ├── external_yara_rules/# 从外部源获取的规则
│   └── file_analysis/      # 自定义文件分析规则
└── README.md               # 本文档
```

**重要提示:** 运行 Morpheus 时，请确保您的当前工作目录是 `Main Files` 目录。

## 工作模式

### 1) VirusTotal 扫描 (在线)

*   **功能**: 向 VirusTotal 提交文件或哈希，使用多个防病毒引擎进行深入分析。此模式使用 VirusTotal 的广泛数据库提供有关潜在威胁的全面信息。
*   **输出**: 提供详细输出，包括安全供应商的见解、社区反馈等。
*   **限制**: API 速率限制 (默认限制相对较高)，对于 VirusTotal 数据库中之前未分析过的文件没有结果。

**在 Morpheus 中的使用**:

1.  通过 [VirusTotal 注册](https://www.virustotal.com/gui/join-us) 注册 VirusTotal。
2.  从您的个人资料中的 "API Key" 获取 API 密钥。
3.  运行 `morpheus_scanner.py`，选择 VirusTotal 扫描选项，并在提示时粘贴您的 API 密钥。

### 2) 默认扫描 (YARA - 离线)

*   **功能**: 使用 YARA 规则 (`yara_rules/`) 和 Pefile (`modules/pe_analysis.py`) 执行静态扫描，识别常见恶意模式。此方法可以快速标记可疑文件，包括 KRYPT0S 的自定义检测。
*   **优势**: 与 "VirusTotal 扫描" 相比，提供增强功能，包括 PDF 输出、AI 集成和访问能够检测未在 VirusTotal 注册的文件的广泛签名数据库。
*   **注意**: 依赖性较重和预设置要求，可能容易不稳定。虽然 Morpheus 经过严格测试，但结果可能因系统而异。

**在 Morpheus 中的使用**:

1.  按照 [安装](#安装) 步骤确保所有依赖项都已安装。
2.  运行 `morpheus_scanner.py` 并选择默认扫描选项，即可使用内置 YARA 规则分析文件。

## 安装与更新

### 安装

要开始使用 Morpheus IOC 扫描器，请按照以下步骤操作：

1.  **克隆仓库 (如果尚未完成)**:
    ```bash
    git clone https://github.com/phantom0004/morpheus_IOC_scanner.git
    cd morpheus_IOC_scanner/Main Files
    ```
    *注意：后续所有命令都应在 `Main Files` 目录下执行。*

2.  **创建并激活虚拟环境 (推荐)**:
    ```bash
    # 使用 conda
    conda create --name IOCscanner python=3.9 -y  # 可替换为其他 Python 3 版本
    conda activate IOCscanner

    # 或者使用 venv
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/macOS
    source venv/bin/activate
    ```

3.  **安装所需的 Python 库**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **设置 YARA 数据库**: Morpheus 自带基本的默认 YARA 规则数据库。要获取更广泛的规则集，请运行设置文件：
    ```bash
    python setup.py
    ```
    *注意：运行 `setup.py` 需要 Git 来安装额外的规则。如果未安装 Git，Morpheus 将尝试为您安装 (可能仅限 Windows)，但建议预先安装 Git 以避免可能的错误。*

5.  **运行主程序**:
    ```bash
    python morpheus_scanner.py
    ```

### 更新 YARA 数据库

定期运行 `database_updater.py` 脚本以获取最新的 YARA 规则，并确保您的数据库与 GitHub 存储库中的最新版本保持同步。

```bash
python database_updater.py
```

如果您想切换到更全面或更轻量级的 YARA 规则集 (如 Fortress Edition 或 Nano Edition，如果可用)，只需再次运行 `setup.py` 脚本。这将处理旧文件的删除，并自动为您设置新的规则集。

## 常见问题 (FAQ)

*   **目录错误**: `[-] 继续之前确保您位于'/Main Files' Morpheus目录！程序已中止。`
    *   **原因**: Morpheus 未从其 `Main Files` 文件夹运行。Morpheus 依赖于相对于 `Main Files` 目录的路径。
    *   **解决方案**: 切换到 `morpheus_IOC_scanner/Main Files` 目录再运行程序。 (`cd path/to/morpheus_IOC_scanner/Main Files`)

*   **Git 使用错误**: `Git可能未正确安装，程序无法访问该命令。这可能是由于安装过程中的系统错误。`
    *   **原因**: 主要是在 Windows 上未安装 Git 或 Git 的路径未添加到环境变量中。`setup.py` 尝试使用 `winget` 安装 Git，但这可能需要重启终端。
    *   **解决方案**: 重启终端并重新运行 `setup.py`。如果问题仍然存在，请从 [Git 官方网站](https://git-scm.com/downloads) 手动安装 Git。

*   **Git RPC 错误**: `RPC Failed ...`
    *   **原因**: 下载大型 YARA 规则库时网络连接缓慢或不稳定。
    *   **解决方案**: 尝试使用 `--depth 1` 克隆存储库以减少下载量：
        ```bash
        git clone --depth 1 https://github.com/phantom0004/morpheus_IOC_scanner.git
        ```
        如果您已经克隆了，可以尝试在 `Main Files` 目录中运行 `python database_updater.py` 或 `python setup.py` 重试。

*   **VirusTotal 资源未找到**: `VirusTotal数据库中未找到请求的资源(文件或URL)。`
    *   **原因**: 文件、URL 或哈希不存在于 VirusTotal 的数据库中 (之前未被扫描过)，或者 API 暂时出现问题。
    *   **解决方案**: 尝试提交文件的哈希 (MD5, SHA-256, SHA-1) 而不是文件本身，有时可以获得结果。如果怀疑是 API 问题，请稍后重试。

## 使用示例 (Morpheus V2)

Morpheus V2 通过扫描实际的 WannaCry 样本进行了测试。如下所示，该工具成功提取了有关文件的关键详细信息，通过 AI 生成的判断提供有价值的见解。此外，VirusTotal API 集成增强了分析，提供了对样本的更深入见解。最后，结果可以编译成 PDF，便于进一步审查和分析进行全面记录。

**YARA 分析示例:**
![YARA Scan Example](placeholder_yara_scan.gif) <!-- 请替换为实际的 YARA 扫描 GIF/图片 -->

**VirusTotal 分析示例:**
![VirusTotal Scan Example](placeholder_vt_scan.gif) <!-- 请替换为实际的 VirusTotal 扫描 GIF/图片 -->

**生成的 PDF 文档片段:**
![PDF Report Snippet](placeholder_pdf_report.png) <!-- 请替换为实际的 PDF 报告截图 -->