#!/usr/bin/env Rscript

library(shiny)
library(DT)
library(gridExtra)
library(grid)
library(shinythemes)
library(shinycssloaders)
library(shinyjs)
library(data.table)

# increase max upload table size
options(shiny.maxRequestSize = 100*1024^2)

stages_list <- read.table("files/stagelabel.txt", sep="\n")
stage <- as.character(stages_list$V1)
stage <- c(stage,"All Stages")
stage <- stage[c(length(stage),1:(length(stage)-1))]
stage <- gsub(":", " ", stage)

# Define UI ----
ui <- fluidPage(

  #HEADER & GENERAL UI
  theme = shinytheme("flatly"),
  a(href='https://zfin.org/',img(src='zfin_img.jpg',height='65',align = "left", style = "margin-top:25px;margin-left:60px;")),
  titlePanel(h1(img(src='zfin_fish.png', height='65', style = "padding-bottom:20px;"), "DEATS: A Zebrafish Cell Type Identification Tool",
             align = "center",
             style = "color:#000000;padding-bottom:5px;margin-left:400px;margin-right:75px;font-family: Book Antigua;",
           ),
            windowTitle = "DEATS: A Zebrafish Cell-Type Identification Tool"
        ),
  sidebarLayout(
    sidebarPanel(width = 4,

      #DEATS GENERAL INFO
      helpText("Welcome to the DEATS RShiny Web App"),
      helpText("Please see our", a("github repo", href="https://github.com/pranavs22/DEATS"), "to learn more about the DEATS project"),
      hr(style = "border-color: #18BC9C;"),

      #DEV STAGE UI
      helpText("1. Choose Developmental Stage", style ="color:#2C3F51;font-weight: bold;padding-bottom:13px;"),
      selectInput("stage",
                  label = NULL,
                  choices = c("",stage),
                  selected = "All Stages"),
      hr(style = "border-color: #18BC9C;"),

      #SINGLE DEG LIST UI
      helpText("2. Upload Single DEG List or Multiple DEG Lists", style ="color:#2C3F51;font-weight: bold;"),
      helpText("A. Paste in Single DEG List", style = "color:#2C3F51;font-weight: bold;padding-top:13px;"),
      actionLink("example_single_deg_lst_link", label="Click here for an example Single DEG List", style = "color: #2C3F51;font-weight: bold;font-size: small;text-align: center;padding-left:10px;"),
      verbatimTextOutput("example_single_deg_lst"),
      textAreaInput("single_deg_lst",
                label = NULL,
                height = "100px",
                placeholder = "e.g. ENSDARG00001\n\tENSDARG00002\n\tENSDARG00003 \n\tENSDARG00004 ..."),

      #MULTI DEG LISTS UI
      helpText("B. Upload Multiple DEG Lists", style = "color:#2C3F51;font-weight:bold;padding-top:20px;"),
      actionLink("example_multi_deg_lst_link", label="Click here to upload an example Multiple DEG List", style = "color: #2C3F51;font-weight: bold;font-size: small;text-align: center;padding-left:10px;"),
      textOutput("loaded_example_multi_deg_lst_message"),
      fileInput("multi_deg_lsts",
                 label = NULL,
                 accept = c(".tsv"),
                 buttonLabel = "Upload"),
       # helpText("Choose PETE Score Filter", helpText("(details", a("here)", href="https://github.com/pranavs22/DEATS", style="font-size: 13px;"), style="font-weight:normal;font-size: 13px"), style ="color: #2C3F51;font-weight: bold;font-size: small;padding-left:10px;"),
       textInput("pete",
                 label = NULL,
                 width = "60px",
                 placeholder = "0",
                 value = 0),
      tags$style(type = 'text/css', '#pete {text-align: center;}'),
      helpText("Information on PETE score and format required for Multiple DEG List uploads can be found", a("here", href="https://github.com/pranavs22/DEATS", style= "font-size: 13px;"), style= "font-size: 13px;text-align:center;padding-top:3px;padding-bottom:-5;"),
      hr(style = "border-color: #18BC9C;"),

      #GO!
      actionButton("action", label = "Go"),
      textOutput("Messages"),
      textOutput("Messages2"),
      tags$style(type = 'text/css', '#loaded_example_multi_deg_lst_message {color: #2C3F51;font-weight: bold;font-size: small;text-align: right;}'),
      inlineCSS(list(".shiny-input-container" = "margin-bottom: 0px",
               "#multi_deg_lsts_progress" = "margin-bottom: 0px",
               ".checkbox" = "margin-top: 0px"))
    ),

    #TAB PANELS UI
    mainPanel(
       tabsetPanel(
         type = "tabs",

         #DEG UI
         tabPanel("DEG", tableOutput("DEG_var")),

         #DEATS UI
         tabPanel("DEATS",
            style = "margin-top:10px;",

            #FILE HANDLING
            column(3,
              selectInput("tsv_num", "Unidentified Cell-Type", choices=NULL, selected = NULL),
              hr(style = "border-color: #18BC9C;"),
              textInput("file_rename", label = "Cell-Type Annotation"),
              actionButton('submit','Submit'),
              helpText("Read more about cell-type annotations", a("here", href="https://github.com/2019-bgmp/bgmp-group-project-scrnaseq_zebrafish/blob/master/Shiny/seve_master/zfin_app/README.md")),
              hr(style = "border-color: #18BC9C;"),
              downloadButton("downloadData", "Download DEATS")),

            #DEATS TABLE UI
            column(7,
              # tableOutput("DEATS_var"),
              dataTableOutput("DEATS_var"),
              textOutput("Messages3")),

            #GENE SYMBOLS UI
            column(1,
              useShinyjs(),
              actionButton('see_sym', 'See Gene Symbols'),
              # tags$style(type = 'text/css', '#see_sym {float: right;}'),
              tableOutput("gene_sym"))
            )
          )
        )
      )
)

# Define server logic ----
server <- function(input, output, session) {


  #SETTING LOGIC OPERATORS
  observeEvent(input$single_deg_lst, {
    system("touch files/text")
    system("echo files/text")
    if (file.exists("files/DEG_Lists")){
          file.remove("files/DEG_Lists")
        }
  }, ignoreInit = TRUE)
  observeEvent(input$multi_deg_lsts, {
    system("touch files/DEG_Lists")
    system("echo files/DEG_Lists")
    if (file.exists("files/text")){
          file.remove("files/text")
        }
  })
  observeEvent(input$example_multi_deg_lst_link, {
    system("touch files/act_link")
    system("touch files/DEG_Lists")
    system("echo files/act_link")
    if (file.exists("files/text")){
          file.remove("files/text")
        }
    output$loaded_example_multi_deg_lst_message <- renderText({
      Sys.sleep(0.45)
      "File Uploaded"
    })
  })
  observeEvent(input$example_single_deg_lst_link, {
    toggle("example_single_deg_lst")
    output$example_single_deg_lst <- renderText({"ENSDARG00000090526\nENSDARG00000019230\nENSDARG00000042905\nENSDARG00000103919\nENSDARG00000037789\nENSDARG00000073742"
    })
  })

  #ACTION BUTTON FUNCTION
  observeEvent(input$action, {

    #SINGLE DEG HANDLING
    if (file.exists("files/text")){

      #SHOW SINGLE DEG TABLE
      output$DEG_var <- renderTable({
        unlist(strsplit(input$single_deg_lst, "\n"))
      })

      #SAVE SINGLE DEG TO A FILE
      output$Messages <- renderText({
        if (file.exists("files/deg.tsv")){
          file.remove("files/deg.tsv")
        }
        var <- paste0(input$single_deg_lst,"\n")
        cat(var, file="files/deg.tsv")
      })

      #EXECUTE SCRIPT
      output$Messages2 <- renderText({
        withProgress(message = 'Making Tables', value = 1, {
          stage_cmd <- input$stage
          if(stage_cmd == "All Stages"){
            stage_cmd = "all_stages"
          }
          if(grepl(" ", stage_cmd, fixed=TRUE)){
            stage_cmd <- gsub(" ","_",stage_cmd)
          }
          cmd <- c("./main.py",
                 "-single_list", "files/deg.tsv",
                 "-stage", "NA",
                 "-pete", "0",
                 "-zfin", "files/zfin_wt_expression.json",
                 "-zfa", "files/zfa_ids.txt",
                 "-bspo", "files/bspo_cleaned.txt",
                 "-stage_file", "files/stagelabel.txt")
          cmd[[5]] <- as.character(req(stage_cmd))
          cmd <- paste(unlist(cmd), collapse=' ')
          system(cmd)
          system("rm -r sym_data || true")
          system("cp -r meta_data sym_data")
        })
      })

      #SHOW SCRIPT DATA OUTPUT
      observe({
        f_lst <- list.files("data/")
        f_lst <- sub(".tsv", "", f_lst, fixed = TRUE)
        updateSelectInput(session, "tsv_num", choices = sort(as.numeric(f_lst)))
        output$DEATS_var <- renderDataTable({ ####renderDataTable
          data_tbl <- read.csv("data/data.tsv", check.names=FALSE, header = FALSE, col.names = c("anatomy.term", "Count"))
          dist_tbl <- read.csv("stats/dist.tsv", col.names = c("anatomy.term", "Count"))
          merged_tbl <- merge(dist_tbl,data_tbl, by = "anatomy.term")
          merged_tbl$not_count.x <- sum(merged_tbl$Count.x) - merged_tbl$Count.x
          merged_tbl$not_count.y <- sum(merged_tbl$Count.y) - merged_tbl$Count.y
          merged_tbl <- merged_tbl[c(1,2,4,3,5)]
          merged_tbl$p.val <- apply(merged_tbl, 1,
                        function(x) {
                          tbl <- matrix(as.numeric(x[2:5]), ncol=2, byrow=T)
                          fisher.test(tbl, alternative="two.sided")$p.value
                        })
          merged_tbl <- merged_tbl[,c(1,4,6)]
          colnames(merged_tbl) <- c("Anatomy Term", "Count","p val")
          merged_tbl <- merged_tbl[order((merged_tbl$"Count"),decreasing = TRUE),]


          merged_tbl$"p val" <- round(merged_tbl$"p val",5)###
          # merged_tbl$"p val" <- format(round(merged_tbl$"p val",5), scientific=T)###
          #format(round(0.000538063809520502,5), scientific=T)

          # merged_tbl
          validate(
                  need(nrow(merged_tbl) > 0, "With these filters there is no data to show")
                         )
          # merged_tbl
          datatable(merged_tbl,rownames = FALSE)
        })
      })

      #SHOW GENE SYMBOLS TOGGLE
      observeEvent(input$see_sym,{
        gene_sym_tbl <- read.table("sym_data/meta_data.tsv", check.names=FALSE, header = FALSE, sep = "\t")
        toggle("gene_sym")
        output$gene_sym <- renderTable({
          gene_sym_tbl$V2
        })
      })

      #RENAME METADATA OUTPUT
      observeEvent(input$submit,{
        output$Messages3 <- renderText({
          # file.rename("meta_data/meta_data.tsv", paste0("meta_data/", input$file_rename, ",", input$stage, ",", Sys.Date(), ".tsv"))
          file.rename("meta_data/meta_data.tsv", paste0("meta_data/", gsub(" ", "_", input$file_rename), ",", gsub(" ", "_", input$stage), ",", Sys.Date(), ".tsv"))
        })
      })

      #DOWNLOAD DATA HANDLING
      output$downloadData <- downloadHandler(
        filename = function() {
          paste0(input$stage, ",", Sys.Date(), ".tsv")
          },
        content = function(file) {
          write.table(read.csv("data/data.tsv", header = FALSE, col.names = c("Anatomy Term", "Count")), file)
          }
      )
    }
    ###################################################################################################################################
    #MULTI_DEG HANDLING
    if (file.exists("files/DEG_Lists")){

      #SHOW MULTI_DEG TABLE
      output$DEG_var <- renderTable({

        req(input$multi_deg_lsts)
        deg_lists_var <- read.table(input$multi_deg_lsts$datapath)
        colnames(deg_lists_var) <-c("pVal", "Average_LogFC", "pct1", "pct2", "pVal (adj)", "un ID Cell-Type", "Gene Name")
        deg_lists_var$PETEScore <- (deg_lists_var$pct1 / deg_lists_var$pct2) * (deg_lists_var$Average_LogFC)
        deg_lists_var$"un ID Cell-Type" <- as.integer(deg_lists_var$"un ID Cell-Type" + 1)
        deg_lists_var <- deg_lists_var[c(6,7,8)]
        if (input$pete != 0){
          deg_lists_var <- setorder(setkey(setDT(deg_lists_var), "un ID Cell-Type"), "un ID Cell-Type", -"PETEScore")[
            ,.SD[1:input$pete], by="un ID Cell-Type"]
        }
        if (input$pete == 0){
          deg_lists_var <- setorder(setkey(setDT(deg_lists_var), "un ID Cell-Type"), "un ID Cell-Type", -"PETEScore")[
            ,.SD[1:length(deg_lists_var$PETEScore)], by="un ID Cell-Type"]
        }
        na.omit(deg_lists_var)
      })

      #USE EXAMPLE FILE
      if (file.exists("files/act_link")){
        output$DEG_var <- renderTable({
          deg_lists_var <- read.table("files/example_deg_lists.tsv")
          colnames(deg_lists_var) <-c("pVal", "Average_LogFC", "pct1", "pct2", "pVal (adj)", "un ID Cell-Type", "Gene Name")
          deg_lists_var$PETEScore <- (deg_lists_var$pct1 / deg_lists_var$pct2) * (deg_lists_var$Average_LogFC)
          deg_lists_var$"un ID Cell-Type" <- as.integer(deg_lists_var$"un ID Cell-Type" + 1)
          deg_lists_var <- deg_lists_var[c(6,7,8)]
          if (input$pete != 0){
            deg_lists_var <- setorder(setkey(setDT(deg_lists_var), "un ID Cell-Type"), "un ID Cell-Type", -"PETEScore")[
              ,.SD[1:input$pete], by="un ID Cell-Type"]
          }
          if (input$pete == 0){
            deg_lists_var <- setorder(setkey(setDT(deg_lists_var), "un ID Cell-Type"), "un ID Cell-Type", -"PETEScore")[
              ,.SD[1:length(deg_lists_var$PETEScore)], by="un ID Cell-Type"]
          }
          na.omit(deg_lists_var)
        })
      }

      #SAVE MULTI_DEG TO A FILE
      output$Messages <- renderText({
        if (file.exists("files/deg_lists.tsv")){
          file.remove("files/deg_lists.tsv")
        }
        inFile <- input$multi_deg_lsts
        file.copy(inFile$datapath, file.path("files", "deg_lists.tsv"))
      })

      #EXECUTE SCRIPT
      output$Messages2 <- renderText({
        withProgress(message = 'Making Tables', value = 1, {
          stage_cmd <- input$stage
          pete_cmd <- input$pete
          if(stage_cmd == "All Stages"){
            stage_cmd = "all_stages"
          }
          if(grepl(" ", stage_cmd, fixed=TRUE)){
            stage_cmd <- gsub(" ","_",stage_cmd)
          }
          cmd <- c("./main.py",
                 "-multiple_lists", "files/deg_lists.tsv",
                 "-stage", "NA",
                 "-pete", "0",
                 "-zfin", "files/zfin_wt_expression.json",
                 "-zfa", "files/zfa_ids.txt",
                 "-bspo", "files/bspo_cleaned.txt",
                 "-stage_file", "files/stagelabel.txt")
           if (file.exists("files/act_link")){
             cmd[[3]] <- "files/example_deg_lists.tsv"
             file.remove("files/act_link")
             system("echo changed_cmd[[3]]")
           }
          cmd[[5]] <- as.character(req(stage_cmd))
          cmd[[7]] <- as.character(pete_cmd)
          cmd <- paste(unlist(cmd), collapse=' ')
          system(cmd)
          system("rm -r sym_data || true")
          system("cp -r meta_data sym_data")
        })
      })

      #SHOW SCRIPT DATA OUTPUT
      observe({
        f_lst <- list.files("data/")
        f_lst <- sub(".tsv", "", f_lst, fixed = TRUE)
        updateSelectInput(session, "tsv_num", choices = sort(as.numeric(f_lst)))
        output$DEATS_var <- renderDataTable({####renderTable
          data_tbl <- read.csv(paste0("data/",input$tsv_num,".tsv"), check.names=FALSE, header = FALSE, col.names = c("anatomy.term", "Count"))
          dist_tbl <- read.csv("stats/dist.tsv", col.names = c("anatomy.term", "Count"))
          merged_tbl <- merge(dist_tbl,data_tbl, by = "anatomy.term")
          merged_tbl$not_count.x <- sum(merged_tbl$Count.x) - merged_tbl$Count.x
          merged_tbl$not_count.y <- sum(merged_tbl$Count.y) - merged_tbl$Count.y
          merged_tbl <- merged_tbl[c(1,2,4,3,5)]
          merged_tbl$p.val <- apply(merged_tbl, 1,
                        function(x) {
                          tbl <- matrix(as.numeric(x[2:5]), ncol=2, byrow=T)
                          fisher.test(tbl, alternative="two.sided")$p.value
                        })
          merged_tbl <- merged_tbl[,c(1,4,6)]
          colnames(merged_tbl) <- c("Anatomy Term", "Count","p val")
          merged_tbl <- merged_tbl[order((merged_tbl$"Count"),decreasing = TRUE),]

          merged_tbl$"p val" <- round(merged_tbl$"p val",5)###
          # merged_tbl$"p val" <- format(round(merged_tbl$"p val",5), scientific=T)###
          # format(round(0.000538063809520502,5), scientific=T)

          # merged_tbl
          validate(
                  need(nrow(merged_tbl) > 0, "With these filters there is no data to show")
                         )
          # merged_tbl
          datatable(merged_tbl,rownames = FALSE)
        })
      })

      #SHOW GENE SYMBOLS TOGGLE
      observeEvent(input$see_sym,{
        gene_sym_tbl <- read.table(paste0("sym_data/",input$tsv_num,".tsv"), check.names=FALSE, header = FALSE, sep = "\t")
        toggle("gene_sym")
        output$gene_sym <- renderTable({
          gene_sym_tbl$V2
        })
      })

      #RENAME METADATA OUTPUT
      observeEvent(input$submit,{
        observeEvent(input$file_rename,{
            # file.rename(paste0("meta_data/",input$tsv_num,".tsv"), paste0("meta_data/", input$file_rename, ",", input$stage, ",", Sys.Date(), ".tsv"))
            # file.rename(paste0("meta_data/",input$tsv_num,".tsv"), paste0("meta_data/", input$file_rename, ",", input$stage, ",", Sys.Date(), ".tsv"))
            file.rename(paste0("meta_data/",input$tsv_num,".tsv"), paste0("meta_data/", gsub(" ", "_", input$file_rename), ",", gsub(" ", "_", input$stage), ",", Sys.Date(), ".tsv"))
          })
      })

      #DOWNLOAD DATA HANDLING
      output$downloadData <- downloadHandler(
        filename = function() {
          paste0(input$stage, ",", Sys.Date(), ".tsv")
          },
        content = function(file) {
          write.table(read.csv(paste0("data/",input$tsv_num,".tsv"), header = FALSE, col.names = c("Anatomy Term", "Count")), file)
          }
      )
    }
})

}

# Run the app ----
shinyApp(ui = ui, server = server)
