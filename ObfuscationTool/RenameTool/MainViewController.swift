//
//  MainViewController.swift
//  RenameTool
//
//  参考 LSUnusedResources：选目录、配选项、一键运行、看日志与 mapping
//

import Cocoa

final class MainViewController: NSViewController, NSTableViewDataSource, NSTableViewDelegate, NSTextViewDelegate {

    // MARK: - UI
    private let projectPathField = NSTextField(string: "")
    private let mapsDirField = NSTextField(string: "")
    private let mappingFileField = NSTextField(string: "")
    private let targetFolderField = NSTextField(string: "")
    private let pbxprojField = NSTextField(string: "")
    private let taskNameField = NSTextField(string: "Task1-Global")
    private let oldPrefixesField = NSTextField(string: "")
    private let newPrefixesField = NSTextField(string: "")
    private let authorField = NSTextField(string: "")

    private let onlyPrefixCheck = NSButton(checkboxWithTitle: "仅替换前缀 (only_modify_prefix)", target: nil, action: nil)
    private let rollbackCheck = NSButton(checkboxWithTitle: "回滚模式 (rollback_mode)", target: nil, action: nil)
    private let reuseMappingCheck = NSButton(checkboxWithTitle: "复用旧 mapping (use_mapping_reuse)", target: nil, action: nil)
    private let currentLevelCheck = NSButton(checkboxWithTitle: "只处理当前层 (only_current_level)", target: nil, action: nil)
    private let copyrightCheck = NSButton(checkboxWithTitle: "更新文件头 Created by", target: nil, action: nil)

    private let scopePopup = NSPopUpButton(frame: .zero, pullsDown: false)
    private let pythonPathField = NSTextField(string: "/usr/bin/python3")
    private let scriptPathField = NSTextField(string: "")

    // 任务预设
    private let presetPopup = NSPopUpButton(frame: .zero, pullsDown: false)
    private var presetLabel: NSTextField?

    // 高级 · 中间词库
    private let advancedToggle = NSButton(title: "▶ 高级 · 中间词库", target: nil, action: nil)
    private let wordPackPopup = NSPopUpButton(frame: .zero, pullsDown: false)
    private var wordPackLabel: NSTextField?
    private let middleWordView = NSTextView()
    private let middleWordScroll = NSScrollView()
    private let middleWordContent = NSStackView()
    private var advancedExpanded = false
    private var applyingPreset = false
    private var loadingWordPack = false

    private let runButton = NSButton(title: "开始混淆", target: nil, action: nil)
    private let stopButton = NSButton(title: "停止", target: nil, action: nil)
    private let loadMappingButton = NSButton(title: "刷新 Mapping", target: nil, action: nil)
    private let openMapsButton = NSButton(title: "打开 Maps 目录", target: nil, action: nil)
    private let helpButton = NSButton(title: "使用说明", target: nil, action: nil)

    private let progress = NSProgressIndicator()
    private let statusLabel = NSTextField(labelWithString: "就绪")
    private let logView = NSTextView()
    private let mappingTable = NSTableView()

    private var mappingRows: [(String, String)] = []
    private var runningProcess: Process?
    private var outputPipe: Pipe?
    private let defaults = UserDefaults.standard

    // Browse buttons we need to enable/disable with their fields
    private var mapsBrowseButton: NSButton?
    private var targetBrowseButton: NSButton?
    private var oldPrefixesLabel: NSTextField?
    private var newPrefixesLabel: NSTextField?
    private var authorLabel: NSTextField?
    private var scopeLabel: NSTextField?

    // MARK: - Word packs (vocabulary styles; not bound to any project)

    private static let wordPackOrder = ["词包A", "词包B", "词包C", "词包D", "自定义"]

    private static let wordPacks: [String: [[String]]] = [
        "词包A": [
            ["Gyrosa", "Optiqa", "Alloyx", "Facet", "Prismi", "Beaml",
             "Glowra", "Pulvex", "Thermi", "Magniq", "Axial", "Nodrix",
             "Shella", "Cerami", "Silvex", "Flecta", "Morpho", "Curvix",
             "Edgeon", "Rayvex", "Glimra", "Lucion", "Halove", "Sphera",
             "Orbita", "Fibron", "Tensiq", "Vistro", "Auralo", "Vibrax"],
            ["Syncra", "Bondix", "Pairon", "Meshra", "Hubvex", "Busion",
             "Pathiq", "Routex", "Porton", "Fluxiq", "Bridgo", "Nexion",
             "Coreon", "Dockra", "Uplinx", "Packon", "Cachex", "Muxora",
             "Gateon", "Chaina", "Bindra", "Tunela", "Pivot", "Loopra",
             "Peeron", "Clust", "Shard", "Relixo", "Pathix", "Netora"],
            ["Tonova", "Audvex", "Vocalx", "Phonix", "Notion", "Memoix",
             "Logvex", "Markon", "Tagvex", "Tracix", "Scenra", "Briefx",
             "Echoza", "Dialox", "Phras", "Timvex", "Moment", "Clipra",
             "Frameo", "Remind", "Hearon", "Talkon", "Voceon", "Summix",
             "Statix", "Agilix", "Calmra", "Readyx", "Flowra", "Clearo"],
        ],
        "词包B": [
            ["Prism", "Forge", "Nexus", "Pulse", "Relay", "Shard", "Spire", "Tether", "Vortex", "Warp",
             "Aegis", "Braid", "Crest", "Drift", "Ember", "Flux", "Glyph", "Hinge", "Iris", "Jolt",
             "Lance", "Mosaic", "Nebula", "Omen", "Pivot", "Quartz", "Ridge", "Surge", "Thorn", "Umbra"],
            ["Bus", "Cache", "Chunk", "Datum", "Edge", "Frame", "Graph", "Heap", "Latch", "Mesh",
             "Queue", "Realm", "Scope", "Trace", "Union", "Vault", "Wave", "Yield", "Batch", "Chain",
             "Delta", "Event", "Field", "Guard", "Hash", "Layer", "Macro", "Patch", "Route", "Stack"],
            ["Async", "Bound", "Cached", "Dense", "Eager", "Fixed", "Global", "Hybrid", "Inline", "Just",
             "Lazy", "Local", "Mutable", "Nested", "Opaque", "Prime", "Quiet", "Static", "Typed", "Ultra",
             "Volatile", "Weak", "Xeno", "Yielded", "Zoned", "Atomic", "Binary", "Coarse", "Direct", "Exact"],
        ],
        "词包C": [
            ["Bridge", "Stone", "Pulse", "Forge", "Vault", "Crest", "Arrow", "Ember", "Prism", "Bloom",
             "Drift", "Shard", "Comet", "Flare", "Haven", "Nexus", "Quartz", "Ridge", "Spire", "Thorn",
             "Vortex", "Amber", "Coral", "Epoch", "Fable", "Glyph", "Harbor", "Ivory", "Jasper", "Lancer"],
            ["Chain", "Frame", "Layer", "Mesh", "Queue", "Stack", "Token", "Block", "Cache", "Guard",
             "Hook", "Scope", "Stage", "Track", "Batch", "Depot", "Kernel", "Matrix", "Module", "Packet",
             "Portal", "Relay", "Router", "Schema", "Signal", "Stream", "Thread", "Tunnel", "Vector", "Cipher"],
            ["Nimble", "Solid", "Sharp", "Bright", "Vivid", "Static", "Fluid", "Crisp", "Dense", "Clean",
             "Smart", "Rapid", "Prime", "Elite", "Ultra", "Turbo", "Micro", "Macro", "Hyper", "Fiber",
             "Pixel", "Cubic", "Polar", "Sonic", "Lunar", "Solar", "Terra", "Cyber", "Neon", "Atlas"],
        ],
        "词包D": [
            ["Orbit", "Tide", "Spark", "Anvil", "Beacon", "Chisel", "Dusk", "Flint", "Gale", "Hearth",
             "Knot", "Loom", "Mist", "Onyx", "Pine", "Quill", "Rune", "Silk", "Torch", "Umbra",
             "Veil", "Wren", "Zephyr", "Aspen", "Bolt", "Clay", "Dawn", "Fern", "Grit", "Halo"],
            ["Agent", "Buffer", "Cell", "Codec", "Core", "Daemon", "Engine", "Filter", "Gate", "Hub",
             "Index", "Joint", "Link", "Map", "Node", "Op", "Pipe", "Proxy", "Ring", "Slot",
             "Span", "Store", "Sync", "Tab", "Unit", "Valve", "View", "Wire", "Zone", "Dock"],
            ["Agile", "Bold", "Clear", "Deep", "Fast", "Grand", "Hard", "Iron", "Keen", "Lean",
             "Main", "New", "Open", "Pure", "Raw", "Safe", "True", "Vast", "Wide", "Zero",
             "Base", "Dual", "Flex", "Gold", "High", "Lite", "Mono", "Next", "Pro", "Swift"],
        ],
    ]

    /// 模式模板：只切换「仅换前缀 / 全量随机」，不写死任何项目前缀。
    private struct TaskPreset {
        let title: String
        let taskName: String
        let onlyModifyPrefix: Bool
        let expandWordBank: Bool
    }

    private let taskPresets: [TaskPreset] = [
        TaskPreset(title: "自定义", taskName: "", onlyModifyPrefix: false, expandWordBank: false),
        TaskPreset(title: "① 仅换前缀（自行填写旧/新前缀）",
                   taskName: "Task-Prefix",
                   onlyModifyPrefix: true,
                   expandWordBank: false),
        TaskPreset(title: "② 全量随机中间词（自行填写前后缀）",
                   taskName: "Task-FullRename",
                   onlyModifyPrefix: false,
                   expandWordBank: false),
        TaskPreset(title: "③ 全量随机 + 打开中间词库",
                   taskName: "Task-FullRename",
                   onlyModifyPrefix: false,
                   expandWordBank: true),
    ]

    // MARK: - Lifecycle

    override func loadView() {
        let v = NSView(frame: NSRect(x: 0, y: 0, width: 1100, height: 820))
        v.wantsLayer = true
        v.layer?.backgroundColor = NSColor.windowBackgroundColor.cgColor
        view = v
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        buildUI()
        restoreDefaults()
        resolveDefaultScriptPath()
        onlyPrefixCheck.state = .off
        reuseMappingCheck.state = .on
        rollbackCheck.state = .off
        currentLevelCheck.state = .off
        copyrightCheck.state = .off
        stopButton.isEnabled = false

        rollbackCheck.target = self
        rollbackCheck.action = #selector(onModeTogglesChanged)
        copyrightCheck.target = self
        copyrightCheck.action = #selector(onModeTogglesChanged)
        onlyPrefixCheck.target = self
        onlyPrefixCheck.action = #selector(onModeTogglesChanged)

        NotificationCenter.default.addObserver(
            self,
            selector: #selector(onFormFieldEdited(_:)),
            name: NSControl.textDidChangeNotification,
            object: nil
        )

        // 占位提示：前缀因项目而异，不由预设写入
        oldPrefixesField.placeholderString = "如 ABC,DEF（项目原有，逗号分隔）"
        newPrefixesField.placeholderString = "如 XYZ（混淆后；全量时通常与旧前缀相同）"
        mapsDirField.placeholderString = "mapping JSON 保存目录（非混淆目标）"
        targetFolderField.placeholderString = "要混淆的子目录；可空=整个 project_path；回滚无用"

        // 默认词包：词包A（通用词风，与具体工程无关）
        loadWordPack(named: "词包A")
        updateModeDependentControls()
    }

    deinit {
        NotificationCenter.default.removeObserver(self)
    }

    // MARK: - UI layout (仿 LSUnusedResources：上配置 / 下结果)

    private func buildUI() {
        let root = NSStackView()
        root.orientation = .vertical
        root.spacing = 10
        root.edgeInsets = NSEdgeInsets(top: 14, left: 16, bottom: 14, right: 16)
        root.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(root)
        NSLayoutConstraint.activate([
            root.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            root.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            root.topAnchor.constraint(equalTo: view.topAnchor),
            root.bottomAnchor.constraint(equalTo: view.bottomAnchor),
        ])

        root.addArrangedSubview(sectionTitle("项目路径"))
        root.addArrangedSubview(row(label: "源码根目录 project_path", field: projectPathField, browse: #selector(browseProject)))
        let mapsRow = row(label: "Mapping 输出目录 maps_dir", field: mapsDirField, browse: #selector(browseMaps), browseOut: &mapsBrowseButton)
        root.addArrangedSubview(mapsRow)
        root.addArrangedSubview(row(label: "Mapping JSON（回滚/复用）", field: mappingFileField, browse: #selector(browseMappingFile)))
        let targetRow = row(label: "目标子目录 target_folder", field: targetFolderField, browse: #selector(browseTarget), browseOut: &targetBrowseButton)
        root.addArrangedSubview(targetRow)
        root.addArrangedSubview(row(label: "pbxproj（可空=自动推导）", field: pbxprojField, browse: #selector(browsePbxproj)))

        root.addArrangedSubview(sectionTitle("任务参数"))

        // 任务预设
        let presetRow = NSStackView()
        presetRow.orientation = .horizontal
        presetRow.spacing = 8
        let pLabel = NSTextField(labelWithString: "任务预设")
        pLabel.setContentHuggingPriority(.defaultHigh, for: .horizontal)
        presetLabel = pLabel
        presetPopup.removeAllItems()
        for p in taskPresets { presetPopup.addItem(withTitle: p.title) }
        presetPopup.target = self
        presetPopup.action = #selector(onPresetChanged)
        presetPopup.setContentHuggingPriority(.defaultHigh, for: .horizontal)
        presetRow.addArrangedSubview(pLabel)
        presetRow.addArrangedSubview(presetPopup)
        let presetHint = NSTextField(labelWithString: "只切换模式，不填前缀；旧/新前缀请按项目自行填写")
        presetHint.textColor = .secondaryLabelColor
        presetHint.font = NSFont.systemFont(ofSize: 11)
        presetRow.addArrangedSubview(presetHint)
        root.addArrangedSubview(presetRow)

        let taskRow = NSStackView()
        taskRow.orientation = .horizontal
        taskRow.spacing = 8
        taskRow.addArrangedSubview(labeledField("任务名", taskNameField, width: 160))
        taskRow.addArrangedSubview(labeledField("旧前缀(必填)", oldPrefixesField, width: 200, labelOut: &oldPrefixesLabel))
        taskRow.addArrangedSubview(labeledField("新前缀(必填)", newPrefixesField, width: 200, labelOut: &newPrefixesLabel))
        root.addArrangedSubview(taskRow)

        let checks = NSStackView()
        checks.orientation = .horizontal
        checks.spacing = 12
        [onlyPrefixCheck, rollbackCheck, reuseMappingCheck, currentLevelCheck].forEach { checks.addArrangedSubview($0) }
        root.addArrangedSubview(checks)

        let headerRow = NSStackView()
        headerRow.orientation = .horizontal
        headerRow.spacing = 8
        headerRow.addArrangedSubview(copyrightCheck)
        scopePopup.removeAllItems()
        scopePopup.addItems(withTitles: ["target_folder", "project"])
        let scopeLbl = NSTextField(labelWithString: "scope")
        scopeLabel = scopeLbl
        headerRow.addArrangedSubview(scopeLbl)
        headerRow.addArrangedSubview(scopePopup)
        headerRow.addArrangedSubview(labeledField("作者", authorField, width: 140, labelOut: &authorLabel))
        root.addArrangedSubview(headerRow)

        // 高级 · 中间词库（默认折叠）
        advancedToggle.bezelStyle = .inline
        advancedToggle.isBordered = false
        advancedToggle.target = self
        advancedToggle.action = #selector(onToggleAdvanced)
        advancedToggle.setContentHuggingPriority(.defaultHigh, for: .horizontal)
        root.addArrangedSubview(advancedToggle)

        middleWordContent.orientation = .vertical
        middleWordContent.spacing = 6
        middleWordContent.isHidden = true

        let packRow = NSStackView()
        packRow.orientation = .horizontal
        packRow.spacing = 8
        let wpLabel = NSTextField(labelWithString: "词包")
        wordPackLabel = wpLabel
        wordPackPopup.removeAllItems()
        wordPackPopup.addItems(withTitles: Self.wordPackOrder)
        wordPackPopup.selectItem(withTitle: "词包A")
        wordPackPopup.target = self
        wordPackPopup.action = #selector(onWordPackChanged)
        packRow.addArrangedSubview(wpLabel)
        packRow.addArrangedSubview(wordPackPopup)
        let packHint = NSTextField(labelWithString: "三组用 --- 分隔，组内逗号分隔；仅全量重命名时生效")
        packHint.textColor = .secondaryLabelColor
        packHint.font = NSFont.systemFont(ofSize: 11)
        packRow.addArrangedSubview(packHint)
        middleWordContent.addArrangedSubview(packRow)

        middleWordScroll.hasVerticalScroller = true
        middleWordScroll.hasHorizontalScroller = false
        middleWordScroll.borderType = .bezelBorder
        middleWordScroll.translatesAutoresizingMaskIntoConstraints = false
        middleWordView.isEditable = true
        middleWordView.isRichText = false
        middleWordView.font = NSFont.monospacedSystemFont(ofSize: 11, weight: .regular)
        middleWordView.delegate = self
        middleWordView.minSize = NSSize(width: 0, height: 0)
        middleWordView.maxSize = NSSize(width: CGFloat.greatestFiniteMagnitude, height: CGFloat.greatestFiniteMagnitude)
        middleWordView.isVerticallyResizable = true
        middleWordView.isHorizontallyResizable = false
        middleWordView.autoresizingMask = [.width]
        if let tc = middleWordView.textContainer {
            tc.containerSize = NSSize(width: 0, height: CGFloat.greatestFiniteMagnitude)
            tc.widthTracksTextView = true
        }
        middleWordScroll.documentView = middleWordView
        middleWordScroll.heightAnchor.constraint(equalToConstant: 110).isActive = true
        middleWordContent.addArrangedSubview(middleWordScroll)
        root.addArrangedSubview(middleWordContent)

        root.addArrangedSubview(sectionTitle("运行环境"))
        root.addArrangedSubview(row(label: "Python", field: pythonPathField, browse: #selector(browsePython)))
        root.addArrangedSubview(row(label: "脚本 Rename_merged.py", field: scriptPathField, browse: #selector(browseScript)))

        let actions = NSStackView()
        actions.orientation = .horizontal
        actions.spacing = 10
        runButton.target = self
        runButton.action = #selector(onRun)
        runButton.bezelStyle = .rounded
        runButton.keyEquivalent = "\r"
        stopButton.target = self
        stopButton.action = #selector(onStop)
        stopButton.bezelStyle = .rounded
        loadMappingButton.target = self
        loadMappingButton.action = #selector(onRefreshMapping)
        openMapsButton.target = self
        openMapsButton.action = #selector(onOpenMaps)
        [runButton, stopButton, loadMappingButton, openMapsButton].forEach { actions.addArrangedSubview($0) }
        progress.style = .spinning
        progress.controlSize = .small
        progress.isDisplayedWhenStopped = false
        actions.addArrangedSubview(progress)
        actions.addArrangedSubview(statusLabel)
        statusLabel.lineBreakMode = .byTruncatingTail
        root.addArrangedSubview(actions)

        // 下方：日志 | Mapping 左右分栏，随窗口拉宽；修 NSTextView 逐字换行
        let logScroll = NSScrollView()
        logScroll.hasVerticalScroller = true
        logScroll.hasHorizontalScroller = true
        logScroll.autohidesScrollers = true
        logScroll.borderType = .bezelBorder
        logScroll.translatesAutoresizingMaskIntoConstraints = false
        logView.isEditable = false
        logView.font = NSFont.monospacedSystemFont(ofSize: 12, weight: .regular)
        logView.minSize = NSSize(width: 0, height: 0)
        logView.maxSize = NSSize(width: CGFloat.greatestFiniteMagnitude, height: CGFloat.greatestFiniteMagnitude)
        logView.isHorizontallyResizable = true
        logView.isVerticallyResizable = true
        logView.autoresizingMask = [.width, .height]
        if let tc = logView.textContainer {
            tc.containerSize = NSSize(width: 0, height: CGFloat.greatestFiniteMagnitude)
            tc.widthTracksTextView = true
        }
        logView.textContainerInset = NSSize(width: 4, height: 4)
        logScroll.documentView = logView

        let mapScroll = NSScrollView()
        mapScroll.hasVerticalScroller = true
        mapScroll.hasHorizontalScroller = true
        mapScroll.autohidesScrollers = true
        mapScroll.borderType = .bezelBorder
        mapScroll.translatesAutoresizingMaskIntoConstraints = false
        mappingTable.headerView = NSTableHeaderView()
        let c1 = NSTableColumn(identifier: NSUserInterfaceItemIdentifier("old"))
        c1.title = "旧类名"
        c1.width = 260
        c1.minWidth = 120
        let c2 = NSTableColumn(identifier: NSUserInterfaceItemIdentifier("new"))
        c2.title = "新类名"
        c2.width = 260
        c2.minWidth = 120
        mappingTable.addTableColumn(c1)
        mappingTable.addTableColumn(c2)
        mappingTable.columnAutoresizingStyle = .uniformColumnAutoresizingStyle
        mappingTable.dataSource = self
        mappingTable.delegate = self
        mappingTable.usesAlternatingRowBackgroundColors = true
        mapScroll.documentView = mappingTable

        let logBox = NSStackView()
        logBox.orientation = .vertical
        logBox.spacing = 4
        logBox.translatesAutoresizingMaskIntoConstraints = false
        logBox.addArrangedSubview(sectionTitle("运行日志"))
        logBox.addArrangedSubview(logScroll)

        let mapBox = NSStackView()
        mapBox.orientation = .vertical
        mapBox.spacing = 4
        mapBox.translatesAutoresizingMaskIntoConstraints = false
        mapBox.addArrangedSubview(sectionTitle("Mapping 结果"))
        mapBox.addArrangedSubview(mapScroll)

        let split = NSSplitView()
        split.isVertical = true  // 左右分栏
        split.dividerStyle = .thin
        split.translatesAutoresizingMaskIntoConstraints = false
        split.addArrangedSubview(logBox)
        split.addArrangedSubview(mapBox)
        // 日志约占 60%，Mapping 约 40%
        split.setHoldingPriority(NSLayoutConstraint.Priority(250), forSubviewAt: 0)
        split.setHoldingPriority(NSLayoutConstraint.Priority(249), forSubviewAt: 1)

        logScroll.setContentHuggingPriority(.defaultLow, for: .horizontal)
        logScroll.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)
        mapScroll.setContentHuggingPriority(.defaultLow, for: .horizontal)
        mapScroll.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)
        logScroll.widthAnchor.constraint(greaterThanOrEqualToConstant: 420).isActive = true
        mapScroll.widthAnchor.constraint(greaterThanOrEqualToConstant: 280).isActive = true

        root.addArrangedSubview(split)
        let h = split.heightAnchor.constraint(greaterThanOrEqualToConstant: 280)
        h.priority = .defaultHigh
        h.isActive = true
        // 让底部区域吃掉剩余纵向空间
        root.setCustomSpacing(12, after: actions)
        split.setContentHuggingPriority(.defaultLow, for: .vertical)

        // 页脚：使用说明固定在窗口右下角
        helpButton.target = self
        helpButton.action = #selector(onOpenHelp)
        helpButton.bezelStyle = .rounded
        helpButton.setContentHuggingPriority(.required, for: .horizontal)
        let footer = NSStackView()
        footer.orientation = .horizontal
        footer.spacing = 8
        let footerSpacer = NSView()
        footerSpacer.setContentHuggingPriority(.defaultLow, for: .horizontal)
        footerSpacer.setContentCompressionResistancePriority(.fittingSizeCompression, for: .horizontal)
        footer.addArrangedSubview(footerSpacer)
        footer.addArrangedSubview(helpButton)
        root.addArrangedSubview(footer)
        root.setCustomSpacing(8, after: split)
    }

    private func sectionTitle(_ text: String) -> NSView {
        let l = NSTextField(labelWithString: text)
        l.font = NSFont.boldSystemFont(ofSize: 13)
        return l
    }

    private func row(label: String, field: NSTextField, browse: Selector, browseOut: UnsafeMutablePointer<NSButton?>? = nil) -> NSView {
        let stack = NSStackView()
        stack.orientation = .horizontal
        stack.spacing = 8
        let l = NSTextField(labelWithString: label)
        l.setContentHuggingPriority(.defaultHigh, for: .horizontal)
        l.widthAnchor.constraint(equalToConstant: 200).isActive = true
        field.isEditable = true
        field.isBordered = true
        field.bezelStyle = .roundedBezel
        let btn = NSButton(title: "浏览…", target: self, action: browse)
        btn.bezelStyle = .rounded
        browseOut?.pointee = btn
        stack.addArrangedSubview(l)
        stack.addArrangedSubview(field)
        stack.addArrangedSubview(btn)
        return stack
    }

    private func labeledField(_ title: String, _ field: NSTextField, width: CGFloat, labelOut: UnsafeMutablePointer<NSTextField?>? = nil) -> NSView {
        let stack = NSStackView()
        stack.orientation = .horizontal
        stack.spacing = 4
        let l = NSTextField(labelWithString: title)
        labelOut?.pointee = l
        field.isBordered = true
        field.bezelStyle = .roundedBezel
        field.widthAnchor.constraint(equalToConstant: width).isActive = true
        stack.addArrangedSubview(l)
        stack.addArrangedSubview(field)
        return stack
    }

    // MARK: - Defaults / paths

    private func restoreDefaults() {
        projectPathField.stringValue = defaults.string(forKey: "project_path") ?? ""
        mapsDirField.stringValue = defaults.string(forKey: "maps_dir") ?? ""
        mappingFileField.stringValue = defaults.string(forKey: "mapping_file") ?? ""
        targetFolderField.stringValue = defaults.string(forKey: "target_folder") ?? ""
        pbxprojField.stringValue = defaults.string(forKey: "pbxproj_path") ?? ""
        oldPrefixesField.stringValue = defaults.string(forKey: "old_prefixes") ?? ""
        newPrefixesField.stringValue = defaults.string(forKey: "new_prefixes") ?? ""
        authorField.stringValue = defaults.string(forKey: "author_name") ?? ""
        pythonPathField.stringValue = defaults.string(forKey: "python_path") ?? "/usr/bin/python3"
        if let s = defaults.string(forKey: "script_path"), !s.isEmpty {
            scriptPathField.stringValue = s
        }
    }

    private func persistDefaults() {
        defaults.set(projectPathField.stringValue, forKey: "project_path")
        defaults.set(mapsDirField.stringValue, forKey: "maps_dir")
        defaults.set(mappingFileField.stringValue, forKey: "mapping_file")
        defaults.set(targetFolderField.stringValue, forKey: "target_folder")
        defaults.set(pbxprojField.stringValue, forKey: "pbxproj_path")
        defaults.set(oldPrefixesField.stringValue, forKey: "old_prefixes")
        defaults.set(newPrefixesField.stringValue, forKey: "new_prefixes")
        defaults.set(authorField.stringValue, forKey: "author_name")
        defaults.set(pythonPathField.stringValue, forKey: "python_path")
        defaults.set(scriptPathField.stringValue, forKey: "script_path")
    }

    private func resolveDefaultScriptPath() {
        let fm = FileManager.default
        let current = scriptPathField.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)

        // 已保存且仍有效（排除 DerivedData 临时产物）则沿用
        if !current.isEmpty, fm.fileExists(atPath: current), !current.contains("/DerivedData/") {
            return
        }

        // 优先 App 包内脚本（DMG /Applications 分发），再回退到源码树 Scripts/
        let sourceTreeScript = URL(fileURLWithPath: #file)
            .deletingLastPathComponent() // RenameTool
            .deletingLastPathComponent() // ObfuscationTool
            .appendingPathComponent("Scripts/Rename_merged.py").path

        var candidates: [String] = []
        if let res = Bundle.main.resourceURL {
            candidates.append(res.appendingPathComponent("Rename_merged.py").path)
            candidates.append(res.appendingPathComponent("Scripts/Rename_merged.py").path)
        }
        candidates.append(Bundle.main.bundlePath + "/Contents/Resources/Rename_merged.py")
        candidates.append(Bundle.main.bundlePath + "/Contents/Resources/Scripts/Rename_merged.py")
        candidates.append(sourceTreeScript)

        for c in candidates where !c.isEmpty {
            if fm.fileExists(atPath: c) {
                scriptPathField.stringValue = c
                defaults.set(c, forKey: "script_path")
                return
            }
        }
    }

    // MARK: - Presets & middle words

    @objc private func onPresetChanged() {
        let idx = presetPopup.indexOfSelectedItem
        guard idx > 0, idx < taskPresets.count else { return } // 0 = 自定义
        if rollbackCheck.state == .on {
            // 回滚中忽略预设应用
            presetPopup.selectItem(at: 0)
            return
        }
        let p = taskPresets[idx]
        applyingPreset = true
        // 仅套用模式开关；不覆盖用户已填的旧/新前缀（各项目前缀不同）
        if !p.taskName.isEmpty {
            taskNameField.stringValue = p.taskName
        }
        onlyPrefixCheck.state = p.onlyModifyPrefix ? .on : .off
        rollbackCheck.state = .off
        reuseMappingCheck.state = .off
        applyingPreset = false
        if p.expandWordBank, !advancedExpanded {
            onToggleAdvanced()
        }
        updateModeDependentControls()
        let prefixHint = oldPrefixesField.stringValue.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            ? " — 请填写旧/新前缀"
            : ""
        statusLabel.stringValue = "已套用模式：\(p.title)\(prefixHint)"
    }

    @objc private func onFormFieldEdited(_ note: Notification) {
        guard !applyingPreset else { return }
        guard let field = note.object as? NSTextField else { return }
        let watched = [taskNameField, oldPrefixesField, newPrefixesField]
        guard watched.contains(where: { $0 === field }) else { return }
        if presetPopup.indexOfSelectedItem != 0 {
            presetPopup.selectItem(at: 0)
        }
    }

    @objc private func onToggleAdvanced() {
        advancedExpanded.toggle()
        middleWordContent.isHidden = !advancedExpanded
        advancedToggle.title = advancedExpanded ? "▼ 高级 · 中间词库" : "▶ 高级 · 中间词库"
    }

    @objc private func onWordPackChanged() {
        let name = wordPackPopup.titleOfSelectedItem ?? "自定义"
        if name == "自定义" { return }
        loadWordPack(named: name)
    }

    private func loadWordPack(named name: String) {
        guard let groups = Self.wordPacks[name] else { return }
        loadingWordPack = true
        middleWordView.string = formatWordGroups(groups)
        loadingWordPack = false
        if wordPackPopup.titleOfSelectedItem != name {
            wordPackPopup.selectItem(withTitle: name)
        }
    }

    private func formatWordGroups(_ groups: [[String]]) -> String {
        groups.map { $0.joined(separator: ", ") }.joined(separator: "\n---\n")
    }

    private func parseMiddleWordGroups() -> [[String]]? {
        let raw = middleWordView.string
            .replacingOccurrences(of: "\r\n", with: "\n")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        guard !raw.isEmpty else { return nil }
        let sections = raw.components(separatedBy: "---")
        var groups: [[String]] = []
        for section in sections {
            let words = section
                .split(whereSeparator: { $0 == "," || $0 == "，" || $0 == ";" || $0 == "\n" || $0 == "\t" })
                .map { String($0).trimmingCharacters(in: .whitespacesAndNewlines) }
                .filter { !$0.isEmpty }
            if !words.isEmpty { groups.append(words) }
        }
        return groups.isEmpty ? nil : groups
    }

    func textDidChange(_ notification: Notification) {
        guard notification.object as? NSTextView === middleWordView else { return }
        guard !loadingWordPack else { return }
        if wordPackPopup.titleOfSelectedItem != "自定义" {
            wordPackPopup.selectItem(withTitle: "自定义")
        }
    }

    // MARK: - Mode-dependent enablement

    @objc private func onModeTogglesChanged() {
        updateModeDependentControls()
    }

    /// rollback_mode 下脚本只读 mapping 并反向还原，不走混淆主流程。
    /// 因此前缀 / 仅替换前缀 / 复用 mapping / 只处理当前层 / 文件头 / target_folder 均无用。
    private func updateModeDependentControls() {
        let rollback = rollbackCheck.state == .on
        let copyrightOn = (!rollback) && (copyrightCheck.state == .on)
        let middleWordsEnabled = (!rollback) && (onlyPrefixCheck.state == .off)

        // Unused in rollback (see Rename_merged.rollback_from_mapping / run_all_tasks)
        setControlEnabled(!rollback, field: oldPrefixesField, label: oldPrefixesLabel)
        setControlEnabled(!rollback, field: newPrefixesField, label: newPrefixesLabel)
        onlyPrefixCheck.isEnabled = !rollback
        reuseMappingCheck.isEnabled = !rollback  // ignored when rollback; disable, keep state
        currentLevelCheck.isEnabled = !rollback
        copyrightCheck.isEnabled = !rollback
        setControlEnabled(!rollback, field: targetFolderField, button: targetBrowseButton)

        // 预设：回滚时禁用
        presetPopup.isEnabled = !rollback
        presetLabel?.textColor = rollback ? .disabledControlTextColor : .labelColor

        // File-header extras only matter when copyright is on (and not rollback)
        scopePopup.isEnabled = copyrightOn
        scopeLabel?.textColor = copyrightOn ? .labelColor : .disabledControlTextColor
        setControlEnabled(copyrightOn, field: authorField, label: authorLabel)

        // 中间词库：仅全量重命名且非回滚
        advancedToggle.isEnabled = middleWordsEnabled
        advancedToggle.contentTintColor = middleWordsEnabled ? .labelColor : .disabledControlTextColor
        wordPackPopup.isEnabled = middleWordsEnabled
        wordPackLabel?.textColor = middleWordsEnabled ? .labelColor : .disabledControlTextColor
        middleWordView.isEditable = middleWordsEnabled
        middleWordView.textColor = middleWordsEnabled ? .textColor : .disabledControlTextColor
        middleWordScroll.alphaValue = middleWordsEnabled ? 1.0 : 0.55

        // Still needed / useful in rollback:
        // project_path, Mapping JSON, pbxproj (fallback), maps_dir (open/refresh), python/script, run
        runButton.title = rollback ? "开始回滚" : "开始混淆"
        statusLabel.stringValue = rollback ? "回滚模式：请确认 Mapping JSON" : "就绪"
    }

    private func setControlEnabled(_ enabled: Bool, field: NSTextField, label: NSTextField? = nil, button: NSButton? = nil) {
        field.isEnabled = enabled
        field.textColor = enabled ? .controlTextColor : .disabledControlTextColor
        label?.textColor = enabled ? .labelColor : .disabledControlTextColor
        button?.isEnabled = enabled
    }

    // MARK: - Browse

    @objc private func browseProject() { pickDir(into: projectPathField) }
    @objc private func browseMaps() {
        // maps_dir 仍是目录；若用户直接点选 .json，则目录填父路径、并写入 Mapping JSON 字段
        let panel = NSOpenPanel()
        panel.canChooseDirectories = true
        panel.canChooseFiles = true
        panel.allowsMultipleSelection = false
        panel.allowedFileTypes = ["json"]
        panel.message = "选择 Mapping 目录，或直接选择一份 .json 映射文件"
        if panel.runModal() == .OK, let url = panel.url {
            var isDir: ObjCBool = false
            FileManager.default.fileExists(atPath: url.path, isDirectory: &isDir)
            if isDir.boolValue {
                mapsDirField.stringValue = url.path
            } else {
                mapsDirField.stringValue = url.deletingLastPathComponent().path
                mappingFileField.stringValue = url.path
            }
        }
    }
    @objc private func browseMappingFile() { pickFile(into: mappingFileField, types: ["json", "txt"]) }
    @objc private func browseTarget() { pickDir(into: targetFolderField) }
    @objc private func browsePbxproj() { pickFile(into: pbxprojField, types: ["pbxproj"]) }
    @objc private func browsePython() { pickFile(into: pythonPathField, types: nil) }
    @objc private func browseScript() { pickFile(into: scriptPathField, types: ["py"]) }

    private func pickDir(into field: NSTextField) {
        let panel = NSOpenPanel()
        panel.canChooseDirectories = true
        panel.canChooseFiles = false
        panel.allowsMultipleSelection = false
        if panel.runModal() == .OK, let url = panel.url {
            field.stringValue = url.path
        }
    }

    private func pickFile(into field: NSTextField, types: [String]?) {
        let panel = NSOpenPanel()
        panel.canChooseDirectories = false
        panel.canChooseFiles = true
        panel.allowsMultipleSelection = false
        if let types = types {
            panel.allowedFileTypes = types
        }
        if panel.runModal() == .OK, let url = panel.url {
            field.stringValue = url.path
        }
    }

    // MARK: - Run

    @objc private func onRun() {
        persistDefaults()
        let project = projectPathField.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)
        let maps = mapsDirField.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)
        let target = targetFolderField.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)
        let script = scriptPathField.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)
        let python = pythonPathField.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)

        let isRollback = rollbackCheck.state == .on
        let mappingFileEarly = mappingFileField.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)

        guard !project.isEmpty else { return alert("请填写 project_path") }
        guard FileManager.default.fileExists(atPath: project) else { return alert("project_path 不存在") }
        guard FileManager.default.fileExists(atPath: script) else { return alert("找不到 Rename_merged.py") }
        guard FileManager.default.isExecutableFile(atPath: python) || FileManager.default.fileExists(atPath: python) else {
            return alert("Python 路径无效")
        }

        if isRollback {
            guard !mappingFileEarly.isEmpty else { return alert("回滚模式请选择 Mapping JSON") }
            guard FileManager.default.fileExists(atPath: mappingFileEarly) else { return alert("Mapping JSON 不存在") }
            // maps_dir / target_folder / 前缀 在回滚中脚本不用；maps 仅用于临时配置旁路，可空则落到 project 旁
        } else {
            guard !maps.isEmpty else { return alert("请填写 maps_dir（mapping JSON 输出目录）") }
            let oldPCheck = splitCSV(oldPrefixesField.stringValue)
            let newPCheck = splitCSV(newPrefixesField.stringValue)
            guard !oldPCheck.isEmpty else { return alert("请填写旧前缀（因项目而异，预设不会自动填）") }
            guard !newPCheck.isEmpty else { return alert("请填写新前缀（因项目而异，预设不会自动填）") }
        }

        let mapsEffective = maps.isEmpty ? (project as NSString).deletingLastPathComponent : maps
        try? FileManager.default.createDirectory(atPath: mapsEffective, withIntermediateDirectories: true)

        // target_folder = 要混淆的子目录（不是 mapping 存放处）。空 → 整个 project_path；回滚时脚本不用，空则占位。
        let targetEffective = target.isEmpty ? project : target

        var task: [String: Any] = [
            "name": taskNameField.stringValue.isEmpty ? "Task1" : taskNameField.stringValue,
            "only_modify_prefix": isRollback ? false : (onlyPrefixCheck.state == .on),
            "rollback_mode": isRollback,
            "use_mapping_reuse": isRollback ? false : (reuseMappingCheck.state == .on),
            "only_current_level": isRollback ? false : (currentLevelCheck.state == .on),
            "target_folder": targetEffective,
        ]
        let oldP = splitCSV(oldPrefixesField.stringValue)
        let newP = splitCSV(newPrefixesField.stringValue)
        if !oldP.isEmpty { task["old_prefixes"] = oldP }
        if !newP.isEmpty { task["new_prefixes"] = newP }
        let pbx = pbxprojField.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)
        if !pbx.isEmpty { task["pbxproj_path"] = pbx }
        let mappingFile = mappingFileField.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)
        if !mappingFile.isEmpty {
            task["rollback_mapping_file"] = mappingFile
            task["input_mapping_file"] = mappingFile
            // 未单独指定 output 时，复用同一文件路径，便于回滚后写回
            if task["output_mapping_file"] == nil {
                task["output_mapping_file"] = mappingFile
            }
        }

        var config: [String: Any] = [
            "project_path": project,
            "maps_dir": mapsEffective,
            "copyright_header": [
                "enabled": copyrightCheck.state == .on,
                "author_name": authorField.stringValue,
                "scope": scopePopup.titleOfSelectedItem ?? "target_folder",
                "scan_header_lines": 30,
            ],
            "tasks": [task],
        ]

        // 全量重命名时把中间词库写入配置（回滚 / 仅前缀不传，脚本用默认）
        if !isRollback, onlyPrefixCheck.state == .off, let groups = parseMiddleWordGroups() {
            config["middle_word_groups"] = groups
        }

        guard let data = try? JSONSerialization.data(withJSONObject: config, options: [.prettyPrinted]) else {
            return alert("无法序列化配置")
        }
        // Fallback temp dir
        let configURL: URL
        do {
            let dir = FileManager.default.temporaryDirectory
            configURL = dir.appendingPathComponent("rename_tool_config_\(UUID().uuidString).json")
            try data.write(to: configURL)
        } catch {
            return alert("写入配置失败: \(error)")
        }

        appendLog("📝 配置已写入: \(configURL.path)\n")
        appendLog(String(data: data, encoding: .utf8) ?? "")
        appendLog("\n—— 开始运行 ——\n")

        let process = Process()
        process.executableURL = URL(fileURLWithPath: python)
        process.arguments = [script, "--config", configURL.path]
        process.currentDirectoryURL = URL(fileURLWithPath: script).deletingLastPathComponent()

        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe
        outputPipe = pipe

        pipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let chunk = handle.availableData
            guard !chunk.isEmpty, let text = String(data: chunk, encoding: .utf8) else { return }
            DispatchQueue.main.async { self?.appendLog(text) }
        }

        process.terminationHandler = { [weak self] proc in
            DispatchQueue.main.async {
                self?.progress.stopAnimation(nil)
                self?.runButton.isEnabled = true
                self?.stopButton.isEnabled = false
                self?.runningProcess = nil
                self?.statusLabel.stringValue = proc.terminationStatus == 0 ? "完成" : "退出码 \(proc.terminationStatus)"
                self?.onRefreshMapping()
                self?.appendLog("\n—— 结束 (code \(proc.terminationStatus)) ——\n")
            }
        }

        do {
            try process.run()
            runningProcess = process
            runButton.isEnabled = false
            stopButton.isEnabled = true
            progress.startAnimation(nil)
            statusLabel.stringValue = "运行中…"
        } catch {
            alert("启动失败: \(error)")
        }
    }

    @objc private func onStop() {
        runningProcess?.terminate()
        statusLabel.stringValue = "已停止"
    }

    @objc private func onOpenMaps() {
        let maps = mapsDirField.stringValue
        guard !maps.isEmpty else { return alert("maps_dir 为空") }
        NSWorkspace.shared.open(URL(fileURLWithPath: maps))
    }

    @objc private func onOpenHelp() {
        let fm = FileManager.default
        let resourceName = "RenameTool-使用说明"
        var candidates: [URL] = []
        if let bundled = Bundle.main.url(forResource: resourceName, withExtension: "html") {
            candidates.append(bundled)
        }
        // Dev / adjacent fallbacks (no project-specific paths)
        let appDir = Bundle.main.bundleURL.deletingLastPathComponent()
        candidates.append(appDir.appendingPathComponent("RenameTool-使用说明.html"))
        candidates.append(appDir.deletingLastPathComponent().appendingPathComponent("RenameTool-使用说明.html"))
        // Source-tree style: …/ObfuscationTool/RenameTool.app → sibling HTML
        candidates.append(Bundle.main.bundleURL
            .deletingLastPathComponent() // …/ObfuscationTool or …/Applications
            .appendingPathComponent("RenameTool-使用说明.html"))
        if let resourceDir = Bundle.main.resourceURL {
            candidates.append(resourceDir.appendingPathComponent("RenameTool-使用说明.html"))
        }
        // Walking up from #file when running from Xcode
        let fromSource = URL(fileURLWithPath: #file)
            .deletingLastPathComponent() // RenameTool/
            .deletingLastPathComponent() // ObfuscationTool/
            .appendingPathComponent("RenameTool-使用说明.html")
        candidates.append(fromSource)

        for url in candidates {
            if fm.fileExists(atPath: url.path) {
                NSWorkspace.shared.open(url)
                return
            }
        }
        alert("未找到使用说明（RenameTool-使用说明.html）")
    }

    @objc private func onRefreshMapping() {
        let maps = mapsDirField.stringValue
        let name = taskNameField.stringValue.isEmpty ? "Task1" : taskNameField.stringValue
        let slug = name.lowercased().replacingOccurrences(of: "[^a-z0-9]+", with: "_", options: .regularExpression)
        let preferred = (maps as NSString).appendingPathComponent("\(slug)_mapping.json")

        var fileToLoad: String?
        if FileManager.default.fileExists(atPath: preferred) {
            fileToLoad = preferred
        } else if let files = try? FileManager.default.contentsOfDirectory(atPath: maps) {
            let jsons = files.filter { $0.hasSuffix("_mapping.json") || $0.hasSuffix(".json") }.sorted()
            fileToLoad = jsons.last.map { (maps as NSString).appendingPathComponent($0) }
        }

        guard let path = fileToLoad, let data = try? Data(contentsOf: URL(fileURLWithPath: path)),
              let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            mappingRows = []
            mappingTable.reloadData()
            appendLog("ℹ️ 未找到 mapping JSON（可先运行一次）\n")
            return
        }

        let dict: [String: String]
        if let m = obj["mapping"] as? [String: String] {
            dict = m
        } else if let m = obj as? [String: String] {
            dict = m
        } else {
            // values might not be strings
            var tmp: [String: String] = [:]
            if let m = obj["mapping"] as? [String: Any] {
                for (k, v) in m { tmp[k] = "\(v)" }
            }
            dict = tmp
        }

        mappingRows = dict.keys.sorted().map { ($0, dict[$0] ?? "") }
        mappingTable.reloadData()
        appendLog("📋 已加载 mapping: \(path)（\(mappingRows.count) 条）\n")
        statusLabel.stringValue = "Mapping \(mappingRows.count) 条"
    }

    // MARK: - Helpers

    private func splitCSV(_ s: String) -> [String] {
        s.split(whereSeparator: { $0 == "," || $0 == "，" || $0 == " " || $0 == ";" })
            .map { String($0).trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
    }

    private func appendLog(_ text: String) {
        let all = NSMutableAttributedString(attributedString: logView.attributedString())
        all.append(NSAttributedString(string: text, attributes: [
            .font: NSFont.monospacedSystemFont(ofSize: 12, weight: .regular),
            .foregroundColor: NSColor.labelColor,
        ]))
        logView.textStorage?.setAttributedString(all)
        logView.scrollToEndOfDocument(nil)
    }

    private func alert(_ message: String) {
        let a = NSAlert()
        a.messageText = message
        a.alertStyle = .warning
        a.runModal()
    }

    // MARK: - Table

    func numberOfRows(in tableView: NSTableView) -> Int { mappingRows.count }

    func tableView(_ tableView: NSTableView, viewFor tableColumn: NSTableColumn?, row: Int) -> NSView? {
        let id = tableColumn?.identifier.rawValue ?? "old"
        let text = id == "new" ? mappingRows[row].1 : mappingRows[row].0
        let cell = NSTextField(labelWithString: text)
        cell.lineBreakMode = .byTruncatingMiddle
        return cell
    }
}
