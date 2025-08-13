if [ "$1" = "run" ] && [ "$2" = "server" ]; then
    uv run src/main.py
elif [ "$1" = "run" ] && [ "$2" = "tests" ]; then
    uv run test_data/testing.py
else
    echo "Invalid command"
    exit 1
fi 