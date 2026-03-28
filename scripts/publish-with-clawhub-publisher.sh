#!/bin/bash
# ClawHub Publisher 发布脚本
# 使用基于PaperMC v2.0.0发布经验创建的自动化工具

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助
show_help() {
    echo "ClawHub Publisher 发布脚本"
    echo "基于PaperMC v2.0.0发布经验创建的自动化工具"
    echo ""
    echo "用法: $0 [选项] <技能路径>"
    echo ""
    echo "选项:"
    echo "  -s, --slug <名称>     技能slug（默认：目录名）"
    echo "  -v, --version <版本>  版本号（默认：从SKILL.md读取）"
    echo "  -n, --name <名称>     显示名称（默认：从SKILL.md读取）"
    echo "  -c, --changelog <文本> 更新日志"
    echo "  -t, --tags <标签>     标签，逗号分隔（默认：latest）"
    echo "  --no-input            非交互模式"
    echo "  --dry-run             试运行，不实际发布"
    echo "  --clean-binary        清理二进制文件"
    echo "  --backup              创建备份"
    echo "  -h, --help            显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 ./my-skill"
    echo "  $0 -s my-skill -v 1.0.0 ./my-skill"
    echo "  $0 --slug my-skill --version 2.0.0 --name \"My Skill\" ./my-skill"
    echo ""
    echo "基于的实践经验:"
    echo "  - PaperMC v2.0.0发布到ClawHub"
    echo "  - 解决版本冲突、文件格式限制、认证问题"
    echo "  - 提供完整的发布工作流和错误处理"
}

# 解析参数
parse_args() {
    POSITIONAL_ARGS=()
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--slug)
                SLUG="$2"
                shift 2
                ;;
            -v|--version)
                VERSION="$2"
                shift 2
                ;;
            -n|--name)
                NAME="$2"
                shift 2
                ;;
            -c|--changelog)
                CHANGELOG="$2"
                shift 2
                ;;
            -t|--tags)
                TAGS="$2"
                shift 2
                ;;
            --no-input)
                NO_INPUT="--no-input"
                shift
                ;;
            --dry-run)
                DRY_RUN="--dry-run"
                shift
                ;;
            --clean-binary)
                CLEAN_BINARY="--clean-binary"
                shift
                ;;
            --backup)
                BACKUP="--backup"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -*|--*)
                print_error "未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                POSITIONAL_ARGS+=("$1")
                shift
                ;;
        esac
    done
    
    # 设置位置参数
    set -- "${POSITIONAL_ARGS[@]}"
    
    # 检查技能路径
    if [ $# -eq 0 ]; then
        print_error "请提供技能路径"
        show_help
        exit 1
    fi
    
    SKILL_PATH="$1"
    
    # 验证路径
    if [ ! -d "$SKILL_PATH" ]; then
        print_error "技能路径不存在或不是目录: $SKILL_PATH"
        exit 1
    fi
}

# 检查环境
check_environment() {
    print_info "检查环境..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi
    
    # 检查clawhub CLI
    if ! command -v clawhub &> /dev/null; then
        print_warning "clawhub CLI 未找到，尝试使用完整路径..."
        
        # 尝试常见路径
        CLAWHUB_PATHS=(
            "/usr/local/bin/clawhub"
            "/usr/bin/clawhub"
            "$HOME/.local/bin/clawhub"
            "/usr/local/lib/nodejs/node-v22.22.1-linux-arm64/bin/clawhub"
        )
        
        for path in "${CLAWHUB_PATHS[@]}"; do
            if [ -f "$path" ]; then
                export PATH="$(dirname "$path"):$PATH"
                print_info "找到 clawhub: $path"
                break
            fi
        done
        
        if ! command -v clawhub &> /dev/null; then
            print_error "请安装 clawhub: npm install -g clawhub"
            exit 1
        fi
    fi
    
    # 检查Python依赖
    print_info "检查Python依赖..."
    cd "$SCRIPT_DIR/skills/clawhub-publisher"
    if [ -f "requirements.txt" ]; then
        if ! python3 -c "import requests, yaml" &> /dev/null; then
            print_warning "缺少Python依赖，正在安装..."
            pip install -r requirements.txt 2>/dev/null || {
                print_error "安装Python依赖失败"
                print_info "请手动运行: pip install -r $SCRIPT_DIR/skills/clawhub-publisher/requirements.txt"
            }
        fi
    fi
    
    print_success "环境检查完成"
}

# 准备技能
prepare_skill() {
    print_info "准备技能..."
    
    local prep_args=("--path" "$SKILL_PATH")
    
    if [ -n "$VERSION" ]; then
        prep_args+=("--version" "$VERSION")
    fi
    
    if [ -n "$CLEAN_BINARY" ]; then
        prep_args+=("--clean-binary")
    fi
    
    if [ -n "$BACKUP" ]; then
        prep_args+=("--backup")
    fi
    
    cd "$SCRIPT_DIR/skills/clawhub-publisher"
    python3 prepare_skill.py "${prep_args[@]}"
    
    if [ $? -eq 0 ]; then
        print_success "技能准备完成"
    else
        print_error "技能准备失败"
        exit 1
    fi
}

# 发布技能
publish_skill() {
    print_info "发布技能..."
    
    local pub_args=("--path" "$SKILL_PATH")
    
    if [ -n "$SLUG" ]; then
        pub_args+=("--slug" "$SLUG")
    fi
    
    if [ -n "$VERSION" ]; then
        pub_args+=("--version" "$VERSION")
    fi
    
    if [ -n "$NAME" ]; then
        pub_args+=("--name" "$NAME")
    fi
    
    if [ -n "$CHANGELOG" ]; then
        pub_args+=("--changelog" "$CHANGELOG")
    fi
    
    if [ -n "$TAGS" ]; then
        pub_args+=("--tags" "$TAGS")
    fi
    
    if [ -n "$NO_INPUT" ]; then
        pub_args+=("--no-input")
    fi
    
    if [ -n "$DRY_RUN" ]; then
        pub_args+=("--dry-run")
    fi
    
    cd "$SCRIPT_DIR/skills/clawhub-publisher"
    python3 publish_skill.py "${pub_args[@]}"
    
    if [ $? -eq 0 ]; then
        print_success "技能发布完成"
    else
        print_error "技能发布失败"
        exit 1
    fi
}

# 主函数
main() {
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    
    print_info "========================================"
    print_info "ClawHub Publisher 发布脚本"
    print_info "基于PaperMC v2.0.0发布经验"
    print_info "========================================"
    echo ""
    
    # 解析参数
    parse_args "$@"
    
    # 显示技能信息
    print_info "技能路径: $SKILL_PATH"
    if [ -n "$SLUG" ]; then
        print_info "技能slug: $SLUG"
    fi
    if [ -n "$VERSION" ]; then
        print_info "版本: $VERSION"
    fi
    echo ""
    
    # 检查环境
    check_environment
    
    # 准备技能
    prepare_skill
    
    # 发布技能
    publish_skill
    
    echo ""
    print_success "发布流程完成！"
    print_info "技能地址: https://clawhub.ai/skills/${SLUG:-$(basename "$SKILL_PATH")}"
}

# 运行主函数
main "$@"