#!/bin/bash
# Simple wrapper for Fabric workspace management
# Usage: ./fabric-cli.sh [command] [args...]

# Load environment variables
set -a
source .env
set +a

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function to show usage
show_help() {
    echo -e "${BLUE}Fabric Workspace Management CLI${NC}"
    echo ""
    echo "Usage: ./fabric-cli.sh [command] [options]"
    echo ""
    echo -e "${GREEN}Common Commands:${NC}"
    echo "  list                              List all workspaces"
    echo "  list --details                    List workspaces with full details"
    echo "  create <name> -e <env>            Create a workspace (env: dev/test/prod)"
    echo "  create-set <project-name>         Create dev/test/prod workspaces"
    echo "  delete <workspace-id>             Delete a workspace"
    echo "  get <workspace-id>                Get workspace details"
    echo ""
    echo -e "${GREEN}User Management:${NC}"
    echo "  add-user <ws-id> <email> --role <role>    Add user (Admin/Member/Contributor/Viewer)"
    echo "  list-users <workspace-id>                  List all users in workspace"
    echo "  remove-user <ws-id> <user-id>              Remove user from workspace"
    echo ""
    echo -e "${GREEN}Bulk Operations:${NC}"
    echo "  delete-bulk --file <file>         Delete workspaces from file"
    echo "  delete-all -e <env>               Delete all workspaces in environment"
    echo ""
    echo -e "${GREEN}Shortcuts:${NC}"
    echo "  ls                                Alias for 'list'"
    echo "  lsd                               Alias for 'list --details'"
    echo "  help                              Show this help message"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./fabric-cli.sh list"
    echo "  ./fabric-cli.sh create-set analytics"
    echo "  ./fabric-cli.sh add-user abc123 user@example.com --role Admin"
    echo ""
}

# Handle shortcuts and aliases
case "$1" in
    help|--help|-h)
        show_help
        exit 0
        ;;
    ls)
        shift
        python3 ops/scripts/manage_workspaces.py list "$@"
        ;;
    lsd)
        shift
        python3 ops/scripts/manage_workspaces.py list --details "$@"
        ;;
    *)
        # Run the command as-is
        python3 ops/scripts/manage_workspaces.py "$@"
        ;;
esac
