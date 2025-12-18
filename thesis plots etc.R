
data <- read.csv("merged_energy_weather_data.csv")
attach(data)
str(data)
colnames(data) <- c("date", "price", "temp", "precip", "wind", "humidity", "cloud", "radiation", "week_day", "month", "day_month")
data$date <- as.Date(data$date, format = "%m/%d/%Y")
data$week_day <- as.factor(data$week_day)
data$month <- as.factor(data$month)
data$day_month <- as.factor(data$day_month)

plot(data$date, data$price,
     type = "l",
     col = "darkblue",
     lwd = 0.7,                             # thinner line for readability
     xlab = "Date",
     ylab = "Price (EUR/MWh)",              # add units
     main = "DK1 Day-Ahead Electricity Prices, 2015–2025",
     xaxt = "n")                            # suppress default x-axis

# Custom x-axis ticks (every 2 years for clarity)
axis(1, at = as.Date(c("2015-01-01", "2017-01-01", "2019-01-01",
                       "2021-01-01", "2023-01-01", "2025-01-01")),
     labels = c("2015", "2017", "2019", "2021", "2023", "2025"))


library(dplyr)
library(ggplot2)

data_2022 <- data %>%
  filter(date >= as.Date("2022-01-01") & date <= as.Date("2022-12-31"))

ggplot(data_2022, aes(x = date, y = price)) +
  geom_line(color = "firebrick", size = 0.4) +          # crisis emphasized in red
  geom_hline(yintercept = 0, linetype = "dashed", color = "grey50") +  # mark 0 line
  labs(title = "DK1 Day-Ahead Electricity Prices in 2022",
       x = "Date", y = "Price (EUR/MWh)") +
  theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold"),
    axis.text = element_text(size = 10))

boxplot(price ~ week_day, data = data,
        main = "Price by Weekday",
        xlab = "Day of Week", ylab = "Price (EUR/MWh)",
        names = c("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"),
        col = "lightgrey", border = "black")


boxplot(price ~ month, data = data,
        main = "Price by Month",
        xlab = "Month", ylab = "Price (EUR/MWh)",
        names = c("Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
        col = "lightgrey", border = "black")


boxplot(price ~ day_month, data = data,
        main = "Price by Day of Month",
        xlab = "Day of Month", ylab = "Price (EUR/MWh)",
        col = "lightgrey", border = "black")



ggplot(data, aes(x = date, y = temp)) +
  geom_line(color = "darkred", size = 0.4) +
  labs(title = "Daily Average Temperature in DK1 (2015–2025)",
       x = "Date", y = "Temperature (°C)") +
  theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold"),
    axis.text = element_text(size = 10)
  )

library(ggplot2)
library(scales)

ggplot(data, aes(x = date, y = temp)) +
  geom_line(color = "darkred", size = 0.4) +
  scale_x_date(date_breaks = "1 year", date_labels = "%Y") +
  scale_y_continuous(breaks = seq(-10, 30, 5),
                     name = "Temperature (°C)") +
  labs(title = "Daily Average Temperature in DK1 (2015–2025)",
       x = "Year") +
  theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold"),
    axis.text = element_text(size = 10)
  )






library(ggplot2)
library(dplyr)
library(scales)
library(purrr)
# ---- 1) Metadata for variables: name, pretty title, y-axis label, optional y breaks
vars_meta <- tribble(
  ~var,                   ~title,                                                         ~ylab,                          
  "humidity",   "Daily Average Relative Humidity (2015–2025)",                   "Relative Humidity (%)",            
  "radiation",  "Daily Average Intensity of Shortwave Radiation (2015–2025)",    "Shortwave Radiation (W/m²)",       
  "wind",       "Daily Average Wind Speed (2015–2025)",                          "Wind Speed (m/s)",                 
  "precip",     "Daily Average Precipitation (2015–2025)",                       "Precipitation (kg/m²)",            
  "cloud",      "Daily Average Cloud Cover (2015–2025)",                         "Cloud Cover (%)",                 
)


# ---- 2) Helper to make a consistent time-series plot
make_series_plot <- function(df, var, title, ylab, ybreaks = NULL, color = "black") {
  p <- ggplot(df, aes(x = date, y = .data[[var]])) +
    geom_line(color = color, linewidth = 0.35) +
    scale_x_date(date_breaks = "1 year", date_labels = "%Y") +
    labs(title = title, x = "Year", y = ylab) +
    theme_minimal(base_size = 11) +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold"),
      axis.text = element_text(size = 9)
    )
  if (!is.null(ybreaks)) {
    p <- p + scale_y_continuous(breaks = ybreaks[[1]])
  }
  p
}


# ---- 3) Generate a list of ggplots (prints to screen); set colors per variable if you like
# Colors chosen to be distinct yet subdued for appendix
colors <- c(
  humidity   = "#1f77b4",  # blue
  radiation  = "#9467bd",  # purple
  wind       = "#2ca02c",  # green
  precip     = "#17becf",  # cyan
  cloud      = "#7f7f7f"   # grey
)

plots <- vars_meta %>%
  mutate(
    plot = pmap(
      list(var, title, ylab),
      ~ make_series_plot(
        df = data,
        var = ..1,
        title = ..2,
        ylab = ..3,
        color = colors[[..1]]
      )
    )
  )

# Print them (in order)
walk(plots$plot, print)




numeric_vars <- sapply(data, is.numeric)
cor_matrix <- cor(data[, numeric_vars], use = "complete.obs")
cor_with_price <- cor_matrix["price", ]
cor_with_price
sort(cor_with_price, decreasing = TRUE)




acf(data$price, lag.max = 30, main = "Autocorrelation of DK1 Day-Ahead Prices")
pacf(data$price, lag.max = 30, main = "Partial Autocorrelation of DK1 Day-Ahead Prices")




# Example schematic (not actual data)
df <- data.frame(
  day = 1:384,
  type = c(rep("Training", 100), rep("Test", 14),
           rep("Training", 114), rep("Test", 14),
           rep("Training", 128), rep("Test", 14))
)

df$block <- rep(1:3, times = c(114, 128, 142))  # three iterations

ggplot(df, aes(x = day, y = block, fill = type)) +
  geom_tile(color = "white") +
  scale_fill_manual(values = c("Training" = "steelblue", "Test" = "firebrick")) +
  labs(
    title = "Expanding Window Cross-Validation (Schematic)",
    x = "Time (days)", y = "Iteration"
  ) +
  theme_minimal()






library(ggplot2)

# Parameters
total_days <- 500  # just for illustration (shorter than your full dataset)
train_init <- 365
horizon <- 14
n_iter <- 5  # show first 5 iterations for clarity

# Build data frame for plotting
plot_data <- data.frame()
for (i in 0:(n_iter-1)) {
  train_end <- train_init + i * horizon
  test_end <- train_end + horizon
  
  # Training block
  train_block <- data.frame(
    day = 1:train_end,
    iteration = paste("Iteration", i+1),
    type = "Training"
  )
  
  # Test block
  test_block <- data.frame(
    day = (train_end+1):test_end,
    iteration = paste("Iteration", i+1),
    type = "Test"
  )
  
  plot_data <- rbind(plot_data, train_block, test_block)
}

# Plot schematic
ggplot(plot_data, aes(x = day, y = iteration, fill = type)) +
  geom_tile(color = "white") +
  scale_fill_manual(values = c("Training" = "steelblue", "Test" = "firebrick")) +
  labs(
    title = "Expanding Window Cross-Validation (365-day initial, 14-day steps)",
    x = "Time (days)", y = "Cross-validation iteration"
  ) +
  theme_minimal()
