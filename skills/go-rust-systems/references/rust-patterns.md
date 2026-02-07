# Rust Patterns

## Ownership & Borrowing

```rust
// Ownership rules
let s = String::from("hello");
let s1 = s;  // s moved to s1, s is no longer valid

// Borrowing - immutable
fn calculate_length(s: &String) -> usize {
    s.len()
}
let s1 = String::from("hello");
let len = calculate_length(&s1);  // s1 still valid

// Borrowing - mutable
fn append_world(s: &mut String) {
    s.push_str(", world!");
}
let mut s = String::from("hello");
append_world(&mut s);
```

## Lifetimes

```rust
// Explicit lifetimes
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

// Struct with lifetime
struct User<'a> {
    name: &'a str,
    email: &'a str,
}

// Static lifetime
const CONFIG: &'static str = "config";
```

## Error Handling

```rust
use thiserror::Error;
use anyhow::{Result, Context};

// Define errors with thiserror (for libraries)
#[derive(Error, Debug)]
pub enum AppError {
    #[error("User not found: {0}")]
    NotFound(String),
    
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
    
    #[error("Invalid input: {0}")]
    Validation(String),
}

// Use anyhow for applications
fn process_user(id: &str) -> Result<User> {
    let user = find_user(id)
        .context("Failed to find user")?;
    Ok(user)
}

// Pattern matching on Result
match parse_number(input) {
    Ok(n) => println!("Parsed: {}", n),
    Err(e) => eprintln!("Error: {}", e),
}
```

## Option Handling

```rust
// Option methods
let value = Some(5);

// map - transform inner value
let doubled = value.map(|x| x * 2);  // Some(10)

// and_then - chain operations
let result = value.and_then(|x| Some(x + 1));

// unwrap_or - provide default
let val = value.unwrap_or(0);

// ok_or - convert to Result
let result: Result<i32, &str> = value.ok_or("No value");

// if let - conditional extraction
if let Some(x) = value {
    println!("Got: {}", x);
}
```

## Async/Await

```rust
use tokio;

#[tokio::main]
async fn main() -> Result<()> {
    let result = fetch_data("https://api.acme.com/data").await?;
    println!("{:?}", result);
    Ok(())
}

async fn fetch_data(url: &str) -> Result<Data> {
    let response = reqwest::get(url).await?;
    let data = response.json::<Data>().await?;
    Ok(data)
}

// Concurrent execution
let (users, products) = tokio::join!(
    fetch_users(),
    fetch_products()
);
```

## Iterators

```rust
let numbers = vec![1, 2, 3, 4, 5];

// map and collect
let doubled: Vec<i32> = numbers.iter().map(|x| x * 2).collect();

// filter
let evens: Vec<&i32> = numbers.iter().filter(|x| *x % 2 == 0).collect();

// fold (reduce)
let sum: i32 = numbers.iter().fold(0, |acc, x| acc + x);

// method chaining
let result: Vec<i32> = numbers
    .iter()
    .filter(|x| *x % 2 == 0)
    .map(|x| x * 2)
    .collect();
```

## Structs and Enums

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: uuid::Uuid,
    pub name: String,
    pub email: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub avatar_url: Option<String>,
}

impl User {
    pub fn new(name: String, email: String) -> Self {
        Self {
            id: uuid::Uuid::new_v4(),
            name,
            email,
            avatar_url: None,
        }
    }
}

// Enum with data
#[derive(Debug)]
pub enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(u8, u8, u8),
}

// Pattern matching
fn handle_message(msg: Message) {
    match msg {
        Message::Quit => println!("Quit"),
        Message::Move { x, y } => println!("Move to ({}, {})", x, y),
        Message::Write(s) => println!("Write: {}", s),
        Message::ChangeColor(r, g, b) => println!("Color: #{:02x}{:02x}{:02x}", r, g, b),
    }
}
```

## Testing

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    #[should_panic(expected = "overflow")]
    fn test_overflow() {
        add(u32::MAX, 1);
    }

    // Async test
    #[tokio::test]
    async fn test_async_fetch() {
        let result = fetch_data("test").await;
        assert!(result.is_ok());
    }
}
```

## Cargo.toml Best Practices

```toml
[package]
name = "my-app"
version = "0.1.0"
edition = "2021"
rust-version = "1.75"

[dependencies]
tokio = { version = "1.35", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
anyhow = "1.0"
thiserror = "1.0"

[dev-dependencies]
tokio-test = "0.4"
mockall = "0.12"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true
```
