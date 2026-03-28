# ClawHub技能工作流

## 项目概述

这是为OpenClaw社区设计的技能开发标准化工作流仓库。基于我们在Moltbook和PaperMC项目中的实践经验，提供完整的技能开发、测试、发布流程。

## 目标

1. **标准化流程**: 提供一致的技能开发体验
2. **质量保证**: 确保技能质量和安全性
3. **社区协作**: 便于团队协作和贡献
4. **持续集成**: 自动化测试和发布

## 仓库结构

```
clawhub-skill-workflow/
├── skills/            # 完整技能
│   └── clawhub-publisher/  # ClawHub发布自动化工具
├── templates/         # 技能模板
├── scripts/          # 开发脚本
├── docs/            # 文档
├── examples/        # 示例技能
└── tests/           # 测试工具
```

## 快速开始

### 1. 创建新技能
```bash
./scripts/create-skill.sh my-new-skill
```

### 2. 开发技能
```bash
cd skills/my-new-skill
# 编辑SKILL.md和相关文件
```

### 3. 测试技能
```bash
./scripts/test-skill.sh my-new-skill
```

### 4. 发布到ClawHub
```bash
# 使用ClawHub Publisher技能
cd skills/clawhub-publisher
python3 publish_skill.py --path ../my-new-skill --slug my-new-skill --version 1.0.0
```

## 🚀 ClawHub Publisher技能

基于PaperMC v2.0.0发布经验创建的自动化发布工具，解决ClawHub发布中的常见问题。

### 核心功能
- **环境检查**: 验证ClawHub CLI、认证、网络等
- **技能准备**: 验证SKILL.md格式、清理非文本文件、检查大小限制
- **智能发布**: 处理版本冲突、重试机制、验证发布结果
- **最佳实践**: 包含完整的发布工作流和错误处理

### 快速使用
```bash
# 方法1: 使用包装脚本（推荐）
./scripts/publish-with-clawhub-publisher.sh --slug your-skill --version 1.0.0 /path/to/skill

# 方法2: 直接使用Python脚本
# 1. 检查环境
python3 skills/clawhub-publisher/check_clawhub_setup.py

# 2. 准备技能
python3 skills/clawhub-publisher/prepare_skill.py --path /path/to/skill --version 1.0.0

# 3. 发布技能
python3 skills/clawhub-publisher/publish_skill.py --path /path/to/skill --slug your-skill --version 1.0.0
```

### 解决的问题
1. **版本冲突**: 自动检测并建议新版本
2. **文件格式**: 检查和清理非文本文件
3. **认证问题**: 验证ClawHub登录状态
4. **网络问题**: 重试机制和超时处理
5. **验证发布**: 发布后自动验证结果

## 基于的实践经验

### 从Moltbook项目学习:
- 跨时区内容发布策略
- 深度内容与社区讨论的结合
- 密码学验证的技术设计

### 从PaperMC项目学习:
- 服务器自动化管理
- 安全性和稳定性考虑
- 用户友好的交互设计

### 从ClawHub发布经验学习:
- **ClawHub Publisher技能**: 基于PaperMC v2.0.0发布经验创建的自动化发布工具
- 解决版本冲突、文件格式限制、认证问题
- 提供完整的发布工作流和错误处理
- 支持批量发布和CI/CD集成

## 贡献指南

欢迎贡献！请参考:
1. [贡献指南](./docs/CONTRIBUTING.md)
2. [代码规范](./docs/CODE_STYLE.md)
3. [测试指南](./docs/TESTING.md)

## 许可证

MIT

---

*创建: 2026-03-11*
*维护者: YanXi & 小龙女*
*状态: 初始化阶段*
