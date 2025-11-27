// swift-tools-version: 6.1
import PackageDescription

let package = Package(
    name: "swift-summarizer",
    platforms: [.macOS(.v10_15)],
    dependencies: [
        .package(url: "https://github.com/swiftlang/swift-syntax.git", from: "510.0.0"),
    ],
    targets: [
        .executableTarget(
            name: "swift-summarizer",
            dependencies: [
                .product(name: "SwiftSyntax", package: "swift-syntax"),
                .product(name: "SwiftParser", package: "swift-syntax"),
                .product(name: "SwiftSyntaxBuilder", package: "swift-syntax"),
            ]
        ),
    ]
)
