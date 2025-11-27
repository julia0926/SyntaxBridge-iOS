import Foundation
import SwiftSyntax
import SwiftParser
import SwiftSyntaxBuilder

/// A rewriter that strips implementation details from Swift code
class InterfaceSummarizer: SyntaxRewriter {
    let converter: SourceLocationConverter
    
    init(converter: SourceLocationConverter) {
        self.converter = converter
        super.init()
    }
    
    private func getLineComment(for node: SyntaxProtocol) -> Trivia {
        let location = converter.location(for: node.positionAfterSkippingLeadingTrivia)
        return .newlines(1) + .lineComment("// Line: \(location.line)\n")
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
    
    // Simplify variable accessors (computed properties)
    override func visit(_ node: PatternBindingSyntax) -> PatternBindingSyntax {
        guard let accessor = node.accessorBlock else {
            return node
        }
        
        if case .accessors(_) = accessor.accessors {
             // If it has explicit get/set, we might want to keep "get set" but remove bodies
             // This is getting complex, let's stick to functions for now as they are the main noise
        }
        
        return node
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
            
            let rewriter = InterfaceSummarizer(converter: converter)
            let modified = rewriter.visit(sourceFile)
            
            print(modified.description)
        } catch {
            print("Error reading or parsing file: \(error)")
            exit(1)
        }
    }
}
