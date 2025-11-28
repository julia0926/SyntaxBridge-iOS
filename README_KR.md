# SyntaxBridge-iOS 🌉

## 💡 소개

**Swift 및 Objective-C 혼합 프로젝트를 위한 지능형 컨텍스트 최적화 도구**

대규모 iOS 프로젝트에서 수천 줄의 원본 코드를 그대로 탐색하면 **정확도가 떨어지고 불필요한 탐색 비용이 증가**하며, **막대한 토큰을 소모**하게 됩니다. SyntaxBridge는 **코드 구조도(Project Map)**와 **지능형 요약본(Skeleton Code)**을 제공하여 이러한 문제를 해결합니다. 이를 통해 LLM은 전체 아키텍처를 명확히 파악하고, **컨텍스트 오염 없이 핵심 로직에만 집중**하여 더 정확하고 효율적인 추론 결과를 얻을 수 있습니다.

## 🚀 주요 기능

### 1. 지능형 요약 (Intelligent Summarization)
파일 전체를 읽는 대신, **선언부(Declarations)**만 추출하고 **구현부(Implementations)**는 숨깁니다.
- **Swift**: `SwiftSyntax`를 사용하여 AST를 **재작성(Rewrite)**합니다. 함수 본문, 프로퍼티 초기값 등을 제거하고 `/* implementation hidden */`으로 대체하여, LLM이 이해하기 쉬운 유효한 Swift "스켈레톤 코드"를 생성합니다.
- **Objective-C**: **Regex 기반 텍스트 스캐닝**을 사용하여 인터페이스, 구현부, 메서드 시그니처를 추출합니다. 복잡한 빌드 설정 없이도 레거시 코드를 견고하게 요약할 수 있습니다.

### 2. 하이브리드 지원
- 최신 **Swift**와 레거시 **Objective-C** 코드를 모두 완벽하게 지원합니다.
- 빌드 과정 없이(Zero-Build) AST를 파싱하여 **0.1초 이내**에 분석을 완료합니다.

### 3. 토큰 절약
- 원본 코드 대비 **약 90%의 토큰을 절약**합니다.
- LLM의 컨텍스트 윈도우를 효율적으로 사용하여 더 많은 파일을 동시에 분석할 수 있게 합니다.

### 4. 정밀 위치 추적
- 요약된 코드에 **라인 넘버 주석**(`// Line: 123`)을 자동으로 주입합니다.
- LLM이 원본 파일에서 함수나 프로퍼티의 정확한 위치를 파악할 수 있게 합니다.
- 필요한 부분만 읽는 부분 읽기(`read_file` with line ranges)를 가능하게 합니다.

### 5. 프로젝트 지도 생성 (Project Map Generation) 🗺️
- 파일 내용을 읽지 않고도 프로젝트 전체의 **구조적 지도**를 생성합니다.
- 모든 클래스, 구조체, 프로토콜, 익스텐션을 아이콘과 함께 목록화합니다.
- LLM이 특정 파일로 들어가기 전에 전체 구조를 먼저 파악할 수 있는 "목차" 역할을 합니다.
- 사용법: `./tools/generate-map.sh`

## 📊 성능 및 검증

### 테스트 환경
- **Swift**: `LargeManager.swift` (~2,000 라인)
- **Objective-C**: `LegacyManager.m` (~2,000 라인)

### 결과
| 항목 | 원본 (Before) | SyntaxBridge (After) | 개선율 |
| :--- | :--- | :--- | :--- |
| **Swift (Manager)** | 81 KB | 17 KB | **~79% 감소** |
| **ObjC (Manager)** | 65 KB | 3 KB | **~95% 감소** |
| **분석 시간** | - | < 0.1s | **즉시 완료** |

- **정확도**: 모든 함수 선언과 프로퍼티가 누락 없이 추출됨을 검증했습니다.
- **안정성**: 일부 빌드 에러가 있는 파일에서도 정상 동작함을 확인했습니다.

## 📦 설치 방법

### 필수 조건
- **Swift** (Xcode 또는 Toolchain 설치 필요)
- **Python 3**

1. 저장소를 클론합니다.
2. 설치 스크립트를 실행합니다.
   ```bash
   ./install.sh
   ```
   이 스크립트는 필요한 Python 의존성을 설치하고, Swift 도구를 빌드하며, 실행 권한을 설정합니다. 또한 에이전트 설정 파일이 있다면 자동으로 규칙을 추가해줍니다.

3. Claude 설정 파일(`.claude.json` 또는 MCP config)에 훅을 등록합니다.
   ```json
   {
     "hooks": {
       "PreToolUse": "/path/to/SyntaxBridge-iOS/hooks/syntax-bridge-hook.sh"
     }
   }
   ```

## 🤖 에이전트 설정 (Cursor, Windsurf, Claude)

AI 에이전트(Cursor, Windsurf, Claude Code 등)가 SyntaxBridge를 효과적으로 활용하게 하려면, 다음 규칙을 프로젝트의 커스텀 지침 파일(예: `.cursorrules`, `.windsurfrules`, `CLAUDE.md`)에 추가하세요. (`install.sh` 실행 시 자동으로 추가를 시도합니다.)

```markdown
# SyntaxBridge Integration Rules

1. **Reading Files**: When reading large Swift or Objective-C files, the system will automatically provide a summarized version via SyntaxBridge. If you need the full implementation of a specific function, use `read_file` with the specific line range indicated by `// Line: ...` comments.

2. **Project Navigation**: When asked to explore the project structure or find specific classes/symbols, DO NOT use `ls -R` or `find`. Instead, execute:
   `./tools/generate-map.sh`
   This provides a high-level map of all classes, structs, and protocols without reading file contents.
```

## 🛠 동작 원리

LLM이 `read_file` 도구를 사용하여 파일을 읽으려 할 때, **SyntaxBridge Hook**이 개입합니다.
1. 파일 크기가 300라인 이상인지 확인합니다.
2. 언어(Swift/ObjC)를 감지하고 적절한 요약 도구(`swift-summarizer` 또는 `objc-summarizer.py`)를 실행합니다.
3. 원본 파일 대신 생성된 **스켈레톤 코드**를 LLM에게 전달합니다.
4. LLM은 전체 구조를 파악하고, 구현 세부 사항이 필요한 경우에만 해당 부분을 요청합니다.

👉 **[상세 예시 보기 (Before & After)](docs/DEMO.md)**

## 📝 라이선스
MIT License
