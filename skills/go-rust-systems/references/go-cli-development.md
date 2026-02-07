# CLI Development

## Using cobra (Recommended)

**Installation:**

```bash
go get -u github.com/spf13/cobra/cobra
```

**Basic CLI Structure:**

```go
package main

import (
    "fmt"
    "os"
    "github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
    Use:   "myapp",
    Short: "My application description",
    Long:  "Long description of my application",
    Run: func(cmd *cobra.Command, args []string) {
        fmt.Println("Hello from myapp")
    },
}

var versionCmd = &cobra.Command{
    Use:   "version",
    Short: "Print version",
    Run: func(cmd *cobra.Command, args []string) {
        fmt.Println("v1.0.0")
    },
}

var processCmd = &cobra.Command{
    Use:   "process [file]",
    Short: "Process a file",
    Args:  cobra.ExactArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        file := args[0]
        dryRun, _ := cmd.Flags().GetBool("dry-run")

        if dryRun {
            fmt.Printf("Would process: %s\n", file)
            return nil
        }

        return processFile(file)
    },
}

func init() {
    rootCmd.AddCommand(versionCmd)
    rootCmd.AddCommand(processCmd)

    processCmd.Flags().BoolP("dry-run", "d", false, "Preview without executing")
}

func main() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintf(os.Stderr, "Error: %v\n", err)
        os.Exit(1)
    }
}
```

## Using urfave/cli (Alternative)

```go
package main

import (
    "fmt"
    "os"
    "github.com/urfave/cli/v2"
)

func main() {
    app := &cli.App{
        Name:  "myapp",
        Usage: "My application",
        Commands: []*cli.Command{
            {
                Name:  "process",
                Usage: "Process a file",
                Flags: []cli.Flag{
                    &cli.StringFlag{
                        Name:     "file",
                        Aliases:  []string{"f"},
                        Usage:    "File to process",
                        Required: true,
                    },
                    &cli.BoolFlag{
                        Name:  "dry-run",
                        Usage: "Preview without executing",
                    },
                },
                Action: func(c *cli.Context) error {
                    file := c.String("file")
                    dryRun := c.Bool("dry-run")

                    if dryRun {
                        fmt.Printf("Would process: %s\n", file)
                        return nil
                    }

                    return processFile(file)
                },
            },
        },
    }

    if err := app.Run(os.Args); err != nil {
        fmt.Fprintf(os.Stderr, "Error: %v\n", err)
        os.Exit(1)
    }
}
```

## CLI Best Practices

```go
// GOOD: Validate inputs early
func validateInput(file string) error {
    if file == "" {
        return fmt.Errorf("file is required")
    }
    if _, err := os.Stat(file); os.IsNotExist(err) {
        return fmt.Errorf("file does not exist: %s", file)
    }
    return nil
}

// GOOD: Use context for cancellation
func processWithContext(ctx context.Context, file string) error {
    select {
    case <-ctx.Done():
        return ctx.Err()
    default:
        return processFile(file)
    }
}

// GOOD: Structured output (JSON flag)
func outputResult(result interface{}, format string) error {
    switch format {
    case "json":
        enc := json.NewEncoder(os.Stdout)
        enc.SetIndent("", "  ")
        return enc.Encode(result)
    case "yaml":
        data, err := yaml.Marshal(result)
        if err != nil {
            return err
        }
        fmt.Print(string(data))
        return nil
    default:
        fmt.Printf("%+v\n", result)
        return nil
    }
}
```
