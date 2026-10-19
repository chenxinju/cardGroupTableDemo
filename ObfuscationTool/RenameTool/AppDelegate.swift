//
//  AppDelegate.swift
//  RenameTool
//

import Cocoa

final class AppDelegate: NSObject, NSApplicationDelegate {
    private var mainWindowController: MainWindowController?

    @objc func applicationSupportsSecureRestorableState(_ app: NSApplication) -> Bool {
        true
    }

    func applicationWillFinishLaunching(_ notification: Notification) {
        Self.trace("willFinishLaunching")
        NSApp.setActivationPolicy(.regular)
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        Self.trace("didFinishLaunching")
        setupMenu()

        let wc = MainWindowController()
        mainWindowController = wc

        DispatchQueue.main.async {
            Self.trace("async showWindow")
            wc.showWindow(nil)
            if let w = wc.window {
                let screen = NSScreen.main ?? NSScreen.screens.first
                if let screen {
                    let vf = screen.visibleFrame
                    let size = NSSize(width: 1100, height: 780)
                    let origin = NSPoint(
                        x: vf.midX - size.width / 2,
                        y: vf.midY - size.height / 2
                    )
                    w.setFrame(NSRect(origin: origin, size: size), display: true)
                }
                w.level = .normal
                w.collectionBehavior = [.moveToActiveSpace, .managed]
                w.makeKeyAndOrderFront(nil)
                w.orderFrontRegardless()
                NSApp.arrangeInFront(nil)
                Self.trace("window visible=\(w.isVisible) frame=\(NSStringFromRect(w.frame)) screen=\(String(describing: screen?.localizedName)) windows=\(NSApp.windows.count)")
            } else {
                Self.trace("wc.window is nil")
            }
            NSApp.activate(ignoringOtherApps: true)
            NSRunningApplication.current.activate(options: [.activateAllWindows, .activateIgnoringOtherApps])
        }
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { true }

    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows flag: Bool) -> Bool {
        mainWindowController?.showWindow(nil)
        NSApp.activate(ignoringOtherApps: true)
        return true
    }

    @objc private func showMainWindowAction(_ sender: Any?) {
        mainWindowController?.showWindow(nil)
        NSApp.activate(ignoringOtherApps: true)
    }

    private func setupMenu() {
        let mainMenu = NSMenu()
        let appItem = NSMenuItem()
        mainMenu.addItem(appItem)
        let appMenu = NSMenu(title: "RenameTool")
        appItem.submenu = appMenu
        appMenu.addItem(withTitle: "关于 RenameTool", action: #selector(NSApplication.orderFrontStandardAboutPanel(_:)), keyEquivalent: "")
        appMenu.addItem(NSMenuItem.separator())
        appMenu.addItem(withTitle: "退出 RenameTool", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")

        let editItem = NSMenuItem()
        mainMenu.addItem(editItem)
        let editMenu = NSMenu(title: "编辑")
        editItem.submenu = editMenu
        editMenu.addItem(withTitle: "剪切", action: #selector(NSText.cut(_:)), keyEquivalent: "x")
        editMenu.addItem(withTitle: "复制", action: #selector(NSText.copy(_:)), keyEquivalent: "c")
        editMenu.addItem(withTitle: "粘贴", action: #selector(NSText.paste(_:)), keyEquivalent: "v")
        editMenu.addItem(withTitle: "全选", action: #selector(NSText.selectAll(_:)), keyEquivalent: "a")

        let windowItem = NSMenuItem()
        mainMenu.addItem(windowItem)
        let windowMenu = NSMenu(title: "窗口")
        windowItem.submenu = windowMenu
        windowMenu.addItem(withTitle: "显示主窗口", action: #selector(showMainWindowAction(_:)), keyEquivalent: "0")
        NSApp.windowsMenu = windowMenu
        NSApp.mainMenu = mainMenu
    }

    private static func trace(_ msg: String) {
        let line = "[\(Date())] \(msg)\n"
        let url = URL(fileURLWithPath: "/Users/zhong/Desktop/renametool_trace.log")
        guard let data = line.data(using: .utf8) else { return }
        if FileManager.default.fileExists(atPath: url.path), let h = try? FileHandle(forWritingTo: url) {
            h.seekToEndOfFile(); h.write(data); try? h.close()
        } else {
            try? data.write(to: url)
        }
        NSLog("RenameTool: %@", msg)
    }
}

final class MainWindowController: NSWindowController {
    private let contentVC = MainViewController()

    convenience init() {
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1100, height: 780),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.title = "RenameTool — iOS 类名混淆"
        window.minSize = NSSize(width: 900, height: 560)
        window.isReleasedWhenClosed = false
        window.backgroundColor = .windowBackgroundColor
        window.isOpaque = true
        window.hasShadow = true

        let placeholder = NSView(frame: NSRect(x: 0, y: 0, width: 1100, height: 780))
        placeholder.wantsLayer = true
        placeholder.layer?.backgroundColor = NSColor.windowBackgroundColor.cgColor
        let label = NSTextField(labelWithString: "正在加载 RenameTool…")
        label.font = .systemFont(ofSize: 18)
        label.translatesAutoresizingMaskIntoConstraints = false
        placeholder.addSubview(label)
        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: placeholder.centerXAnchor),
            label.centerYAnchor.constraint(equalTo: placeholder.centerYAnchor),
        ])
        window.contentView = placeholder
        window.center()

        self.init(window: window)

        DispatchQueue.main.async { [weak self] in
            guard let self, let window = self.window else { return }
            _ = self.contentVC.view
            window.contentViewController = self.contentVC
            AppDelegateTrace.trace("contentViewController attached, view=\(self.contentVC.view.frame)")
        }
    }
}

enum AppDelegateTrace {
    static func trace(_ msg: String) {
        let line = "[\(Date())] \(msg)\n"
        let url = URL(fileURLWithPath: "/Users/zhong/Desktop/renametool_trace.log")
        if let data = line.data(using: .utf8) {
            if FileManager.default.fileExists(atPath: url.path), let h = try? FileHandle(forWritingTo: url) {
                h.seekToEndOfFile(); h.write(data); try? h.close()
            } else {
                try? data.write(to: url)
            }
        }
        NSLog("RenameTool: %@", msg)
    }
}
