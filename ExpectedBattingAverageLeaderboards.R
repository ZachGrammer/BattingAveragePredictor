library(shiny)
library(readr)

ui <- fluidPage(
  titlePanel("Expected Batting Average Leaderboards"),
  fluidRow(
    column(12,
           div(class = "app-col",
               p("This is an application that displays two leaderboards. The first holds the expected batting average that I have calculated based on every ball 
               any player has hit in play this season. The second holds the expected batting average against that I have calculated based on every pitcher the 
               player has had hit in the 2023 MLB season. You can change the minimum number of at bats and batters faced, as well as search for a player's name 
               in the same format they are listed. The code used to predict these values is located on Github.com/ZachGrammer/BattingAveragePredictor." )
           )
    )
  ),
  fluidRow(
    column(6, 
           numericInput("minabs", "Minimum AB", value = 200),
           dataTableOutput("bLeaderboardOutput")
    ),
    column(6, 
           numericInput("minbfs", "Minimum BF", value = 200),
           dataTableOutput("pLeaderboardOutput")
    )
  )
)

server <- function(input, output, session) {
  
  output$bLeaderboardOutput <- renderDataTable({
  minimumabs <- input$minabs
  bLeaderboardMaker(minimumabs)
  })
  
  bLeaderboardMaker <- function(abInput) {
    df <- read_csv("Batters.csv")
    df <- df[, c("Batter", "Batter Name", "BA", "xBA", "AB")]
    df_sorted <- df[df$AB >= abInput,]
    df_sorted <- df_sorted[order(df_sorted$xBA, decreasing = TRUE), ]
    return(df_sorted)
  }
  
  output$pLeaderboardOutput <- renderDataTable({
    minimumabs <- input$minabs
    pLeaderboardMaker(minimumabs)
  })
  
  pLeaderboardMaker <- function(bfInput) {
    df <- read_csv("Pitchers.csv")
    df <- df[, c("Pitcher", "Pitcher Name", "BAA", "xBAA", "BF")]
    df_sorted <- df[df$BF >= bfInput,]
    df_sorted <- df_sorted[order(df_sorted$xBAA, decreasing = FALSE), ]
    return(df_sorted)
  }
}

shinyApp(ui = ui, server = server)
