# SyntaxBridge Demo & Examples

This document demonstrates how **SyntaxBridge** transforms your code to provide intelligent context to LLMs.

## 1. Swift Example

### Original File (`UserProfileViewController.swift`)
The original file contains full implementation details, UI setup code, and logic.

```swift
import UIKit

class UserProfileViewController: UIViewController {
    
    private let userId: String
    
    init(userId: String) {
        self.userId = userId
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        fetchUserData()
    }
    
    private func setupUI() {
        view.backgroundColor = .white
        // ... 50 lines of UI code ...
    }
    
    func fetchUserData() {
        print("Fetching data for user \(userId)")
        // ... Network request logic ...
    }
}
```

### Summarized Output (What the LLM sees)
SyntaxBridge removes the implementation bodies and adds **Line Number Comments**.

```swift
import UIKit

class UserProfileViewController: UIViewController {
    
    private let userId: String
    
// Line: 7
    init(userId: String) {/* implementation hidden */}

// Line: 12
    required init?(coder: NSCoder) {/* implementation hidden */}

// Line: 16
    override func viewDidLoad() {/* implementation hidden */}

// Line: 22
    private func setupUI() {/* implementation hidden */}

// Line: 27
    func fetchUserData() {/* implementation hidden */}
}
```

---

## 2. Objective-C Example

### Original File (`LegacyManager.m`)

```objective-c
#import "LegacyManager.h"

@implementation LegacyManager

- (void)initializeService {
    NSLog(@"Initializing service...");
    // ... Complex logic ...
}

- (NSDictionary *)fetchDataWithID:(NSString *)identifier {
    NSLog(@"Fetching data for %@", identifier);
    // ... Network logic ...
    return @{@"id": identifier};
}

@end
```

### Summarized Output (What the LLM sees)
SyntaxBridge extracts the interface and method signatures using `LibClang`.

```objective-c
// Line: 3
LegacyManager (OBJC_IMPLEMENTATION_DECL) {
  // Line: 5
  initializeService;
  // Line: 10
  fetchDataWithID:;
}
```

## 🎯 Key Benefits

1.  **Structure First**: The LLM understands the class structure and available methods immediately.
2.  **Precise Navigation**: Using the `// Line: ...` comments, the LLM can request to read only the specific function it needs to modify (e.g., "Read lines 27-35").
3.  **Token Efficiency**: Massive reduction in token usage (often >90%), allowing you to fit more files into the context window.
