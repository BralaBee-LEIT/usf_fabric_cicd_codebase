#!/bin/bash
# Enhanced Fabric CLI - Comprehensive wrapper for all framework functionality
# Usage: ./fabric-cli-enhanced.sh [command] [subcommand] [options]

# Load environment variables
set -a
source .env 2>/dev/null || true
set +a

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Helper function to show main help
show_help() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Microsoft Fabric CI/CD Framework - Enhanced CLI v2.0      ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Usage: ./fabric-cli-enhanced.sh [category] [command] [options]"
    echo ""
    echo -e "${GREEN}📁 WORKSPACE MANAGEMENT${NC}"
    echo "  workspace list                    List all workspaces"
    echo "  workspace list --details          List with full details"
    echo "  workspace create <name> -e <env>  Create workspace (dev/test/prod)"
    echo "  workspace get <id>                Get workspace details"
    echo "  workspace delete <id>             Delete workspace"
    echo "  workspace create-set <name>       Create dev/test/prod set"
    echo ""
    echo -e "${GREEN}👥 USER MANAGEMENT${NC}"
    echo "  user add <ws-id> <email> --role <role>    Add user (Admin/Member/Contributor/Viewer)"
    echo "  user list <workspace-id>                   List users in workspace"
    echo "  user remove <ws-id> <user-id>              Remove user from workspace"
    echo ""
    echo -e "${GREEN}📦 DATA PRODUCT ONBOARDING${NC}"
    echo "  onboard <descriptor.yaml>                  Onboard new data product"
    echo "  onboard <descriptor> --feature <ticket>    Create feature workspace"
    echo "  onboard <descriptor> --dry-run             Preview without changes"
    echo ""
    echo -e "${GREEN}📝 FABRIC ITEMS (Lakehouses, Notebooks, Pipelines)${NC}"
    echo "  items list --workspace <ws-name>           List all items"
    echo "  items list --workspace <ws> --type <type>  List specific type"
    echo "  items create --workspace <ws> --name <name> --type <type>"
    echo "  items delete --workspace <ws> --name <name>"
    echo "  items get --workspace <ws> --name <name>"
    echo ""
    echo -e "${GREEN}🔄 GIT INTEGRATION${NC}"
    echo "  git init --workspace <ws-name>             Initialize Git connection"
    echo "  git sync-to-workspace --workspace <ws>     Pull from Git to workspace"
    echo "  git sync-to-git --workspace <ws>           Push from workspace to Git"
    echo "  git status --workspace <ws>                Check Git sync status"
    echo ""
    echo -e "${GREEN}🚀 DEPLOYMENT${NC}"
    echo "  deploy --workspace <ws> --bundle <zip>     Deploy from bundle"
    echo "  deploy --workspace <ws> --git-repo <url>   Deploy from Git"
    echo "  deploy --workspace <ws> --validate-only    Validation mode"
    echo ""
    echo -e "${GREEN}🏥 HEALTH & MONITORING${NC}"
    echo "  health --workspace <ws> -e <env>           Run health check"
    echo "  health --workspace <ws> --output-file <file>  Save health report"
    echo ""
    echo -e "${GREEN}✅ DATA QUALITY & GOVERNANCE${NC}"
    echo "  dq validate --workspace <ws>               Validate DQ rules"
    echo "  dq gate --workspace <ws>                   Run DQ quality gate"
    echo "  contract validate --file <yaml>            Validate data contract"
    echo "  artifacts validate --workspace <ws>        Validate Fabric artifacts"
    echo ""
    echo -e "${GREEN}📊 POWER BI${NC}"
    echo "  powerbi deploy --workspace <ws>            Deploy Power BI reports"
    echo ""
    echo -e "${GREEN}🔍 PURVIEW${NC}"
    echo "  purview scan --workspace <ws>              Trigger Purview scan"
    echo ""
    echo -e "${GREEN}🔧 SHORTCUTS${NC}"
    echo "  ls                                         workspace list"
    echo "  lsd                                        workspace list --details"
    echo "  help                                       Show this help"
    echo "  help <category>                            Show category-specific help"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./fabric-cli-enhanced.sh ls"
    echo "  ./fabric-cli-enhanced.sh onboard data_products/onboarding/my_product.yaml"
    echo "  ./fabric-cli-enhanced.sh items list --workspace dev-workspace"
    echo "  ./fabric-cli-enhanced.sh git sync-to-workspace --workspace my-ws"
    echo "  ./fabric-cli-enhanced.sh deploy --workspace prod-ws --bundle deploy.zip"
    echo ""
    echo -e "${CYAN}For detailed help on a category:${NC}"
    echo "  ./fabric-cli-enhanced.sh help workspace"
    echo "  ./fabric-cli-enhanced.sh help git"
    echo "  ./fabric-cli-enhanced.sh help deploy"
    echo ""
}

# Category-specific help functions
show_workspace_help() {
    echo -e "${BLUE}Workspace Management Commands${NC}"
    echo ""
    echo "Full reference: python ops/scripts/manage_workspaces.py --help"
}

show_items_help() {
    echo -e "${BLUE}Fabric Items Management Commands${NC}"
    echo ""
    echo "Supported item types: Lakehouse, Notebook, DataPipeline, Report, SemanticModel"
    echo ""
    echo "Full reference: python ops/scripts/manage_fabric_items.py --help"
}

show_git_help() {
    echo -e "${BLUE}Git Integration Commands${NC}"
    echo ""
    echo "Actions: init-git, sync-to-workspace, sync-to-git, status"
    echo ""
    echo "Full reference: python ops/scripts/sync_fabric_git.py --help"
}

show_deploy_help() {
    echo -e "${BLUE}Deployment Commands${NC}"
    echo ""
    echo "Modes: standard, promote, validation"
    echo ""
    echo "Full reference: python ops/scripts/deploy_fabric.py --help"
}

# Main command router
case "$1" in
    help|--help|-h)
        if [ -n "$2" ]; then
            case "$2" in
                workspace) show_workspace_help ;;
                items) show_items_help ;;
                git) show_git_help ;;
                deploy) show_deploy_help ;;
                *) show_help ;;
            esac
        else
            show_help
        fi
        exit 0
        ;;
    
    # Shortcuts
    ls)
        shift
        python ops/scripts/manage_workspaces.py list "$@"
        ;;
    lsd)
        shift
        python ops/scripts/manage_workspaces.py list --details "$@"
        ;;
    
    # Workspace commands
    workspace)
        shift
        python ops/scripts/manage_workspaces.py "$@"
        ;;
    
    # User commands
    user)
        shift
        cmd="$1"
        shift
        case "$cmd" in
            add)
                python ops/scripts/manage_workspaces.py add-user "$@"
                ;;
            list)
                python ops/scripts/manage_workspaces.py list-users "$@"
                ;;
            remove)
                python ops/scripts/manage_workspaces.py remove-user "$@"
                ;;
            *)
                echo -e "${RED}Unknown user command: $cmd${NC}"
                echo "Use: ./fabric-cli-enhanced.sh help"
                exit 1
                ;;
        esac
        ;;
    
    # Data product onboarding
    onboard)
        shift
        python ops/scripts/onboard_data_product.py "$@"
        ;;
    
    # Fabric items management
    items)
        shift
        python ops/scripts/manage_fabric_items.py "$@"
        ;;
    
    # Git integration
    git)
        shift
        python ops/scripts/sync_fabric_git.py "$@"
        ;;
    
    # Deployment
    deploy)
        shift
        python ops/scripts/deploy_fabric.py "$@"
        ;;
    
    # Health checks
    health)
        shift
        python ops/scripts/health_check_fabric.py "$@"
        ;;
    
    # Data quality
    dq)
        shift
        cmd="$1"
        shift
        case "$cmd" in
            validate)
                python ops/scripts/validate_dq_rules.py "$@"
                ;;
            gate)
                python ops/scripts/run_dq_gate.py "$@"
                ;;
            *)
                echo -e "${RED}Unknown dq command: $cmd${NC}"
                echo "Use: dq validate or dq gate"
                exit 1
                ;;
        esac
        ;;
    
    # Data contracts
    contract)
        shift
        python ops/scripts/validate_data_contracts.py "$@"
        ;;
    
    # Artifact validation
    artifacts)
        shift
        python ops/scripts/validate_fabric_artifacts.py "$@"
        ;;
    
    # Power BI
    powerbi)
        shift
        python ops/scripts/deploy_powerbi.py "$@"
        ;;
    
    # Purview
    purview)
        shift
        python ops/scripts/trigger_purview_scan.py "$@"
        ;;
    
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
