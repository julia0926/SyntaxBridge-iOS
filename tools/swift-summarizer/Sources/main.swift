import Foundation
import SwiftSyntax
import SwiftParser
import SwiftSyntaxBuilder

/// Enhanced Swift Summarizer v2
/// Aggressive noise reduction for better agent navigation and reduced context pollution
class InterfaceSummarizer: SyntaxRewriter {
    let converter: SourceLocationConverter
    let filePath: String

    init(converter: SourceLocationConverter, filePath: String) {
        self.converter = converter
        self.filePath = filePath
        super.init()
    }

    private func getLineComment(for node: SyntaxProtocol) -> Trivia {
        let location = converter.location(for: node.positionAfterSkippingLeadingTrivia)
        return .newlines(1) + .lineComment("// Line: \(location.line)\n")
    }

    // Strip property initializers AND remove inline comments
    override func visit(_ node: PatternBindingSyntax) -> PatternBindingSyntax {
        var result = node

        // Remove initializer if present
        if node.initializer != nil {
            result = result
                .with(\.initializer, nil)
                .with(\.trailingTrivia, .spaces(1) + .blockComment("/* hidden */"))
        }

        return result
    }

    // Simplify enum cases - remove associated values and raw values
    override func visit(_ node: EnumCaseElementSyntax) -> EnumCaseElementSyntax {
        var result = node

        // Remove associated values (reduces noise from literals)
        if node.parameterClause != nil {
            result = result.with(\.parameterClause, nil)
        }

        // Remove raw values
        if node.rawValue != nil {
            result = result.with(\.rawValue, nil)
        }

        return result
    }
    
    // Strip function bodies
    override func visit(_ node: FunctionDeclSyntax) -> DeclSyntax {
        let lineComment = getLineComment(for: node)
        
        guard let body = node.body else {
            // Even if no body, add line comment
            return DeclSyntax(node.with(\.leadingTrivia, lineComment + node.leadingTrivia))
        }
        
        let newBody = CodeBlockSyntax(
            leftBrace: body.leftBrace,
            statements: CodeBlockItemListSyntax([]),
            rightBrace: body.rightBrace.with(\.leadingTrivia, .blockComment("/* implementation hidden */"))
        )
        
        let newNode = node.with(\.body, newBody)
                          .with(\.leadingTrivia, lineComment + node.leadingTrivia)
        return DeclSyntax(newNode)
    }
    
    // Strip initializer bodies
    override func visit(_ node: InitializerDeclSyntax) -> DeclSyntax {
        let lineComment = getLineComment(for: node)
        
        guard let body = node.body else {
            return DeclSyntax(node.with(\.leadingTrivia, lineComment + node.leadingTrivia))
        }
        
        let newBody = CodeBlockSyntax(
            leftBrace: body.leftBrace,
            statements: CodeBlockItemListSyntax([]),
            rightBrace: body.rightBrace.with(\.leadingTrivia, .blockComment("/* implementation hidden */"))
        )
        
        let newNode = node.with(\.body, newBody)
                          .with(\.leadingTrivia, lineComment + node.leadingTrivia)
        return DeclSyntax(newNode)
    }
    
    // Strip deinitializer bodies
    override func visit(_ node: DeinitializerDeclSyntax) -> DeclSyntax {
        let lineComment = getLineComment(for: node)
        
        guard let body = node.body else {
            return DeclSyntax(node.with(\.leadingTrivia, lineComment + node.leadingTrivia))
        }
        
        let newBody = CodeBlockSyntax(
            leftBrace: body.leftBrace,
            statements: CodeBlockItemListSyntax([]),
            rightBrace: body.rightBrace.with(\.leadingTrivia, .blockComment("/* implementation hidden */"))
        )
        
        let newNode = node.with(\.body, newBody)
                          .with(\.leadingTrivia, lineComment + node.leadingTrivia)
        return DeclSyntax(newNode)
    }
    
}

@main
struct SwiftSummarizer {
    static func main() {
        guard CommandLine.arguments.count > 1 else {
            print("Usage: swift-summarizer <file-path>")
            exit(1)
        }

        let filePath = CommandLine.arguments[1]
        let fileURL = URL(fileURLWithPath: filePath)

        do {
            let source = try String(contentsOf: fileURL, encoding: .utf8)
            let sourceFile = Parser.parse(source: source)
            let converter = SourceLocationConverter(fileName: filePath, tree: sourceFile)

            // Print header with file path for disambiguation
            print("// SyntaxBridge Summary")
            print("// File: \(filePath)")
            print("// ─────────────────────────────────────────")
            print()

            let rewriter = InterfaceSummarizer(converter: converter, filePath: filePath)
            let modified = rewriter.visit(sourceFile)

            // Clean up output by removing excessive blank lines
            let output = modified.description
            let cleaned = cleanOutput(output)
            print(cleaned)
        } catch {
            print("Error reading or parsing file: \(error)")
            exit(1)
        }
    }

    /// Remove excessive blank lines and trailing whitespace
    static func cleanOutput(_ text: String) -> String {
        let lines = text.components(separatedBy: .newlines)
        var result: [String] = []
        var previousWasBlank = false

        for line in lines {
            let trimmed = line.trimmingCharacters(in: .whitespaces)

            // Skip excessive blank lines
            if trimmed.isEmpty {
                if !previousWasBlank {
                    result.append("")
                }
                previousWasBlank = true
            } else {
                result.append(line)
                previousWasBlank = false
            }
        }

        return result.joined(separator: "\n")
    }
}
