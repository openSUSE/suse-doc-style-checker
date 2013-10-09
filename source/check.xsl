<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method = "xml" indent = "yes"  omit-xml-declaration="no"/>

  <xsl:param name="cssfile">checkresult.css</xsl:param>

  <xsl:template name="createid">
    <xsl:param name="node" select="."/>

    <xsl:choose>
      <xsl:when test="$node/@id">
        <xsl:value-of select="$node/@id"/>
      </xsl:when>
      <xsl:when test="$node/title">
        <xsl:value-of select="normalize-space($node/title)"/>
      </xsl:when>
      <xsl:otherwise>
        <!-- ... -->
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="*">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="text()">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="/">
    <xsl:processing-instruction name="xml-stylesheet">type="text/css" href="<xsl:value-of select="$cssfile"/>"</xsl:processing-instruction>
    <xsl:text>&#10;</xsl:text>
    <results>
      <xsl:apply-templates/>
    </results>
  </xsl:template>

  <xsl:template match="procedure">
    <xsl:variable name="steps" select="count(step)"/>
    <xsl:choose>
      <xsl:when test="$steps > 10">
        <result>
          <warning>Procedure <xsl:call-template name="createid"/> has <xsl:value-of select="$steps"/> steps.</warning>
          <expectation>Procedures may contain up to 10 steps.</expectation>
        </result>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="step[11]" mode="old">
    <xsl:param name="id">
      <xsl:choose>
        <xsl:when test="parent::procedure[@id]">
          <xsl:value-of select="parent::procedure/@id"/>
        </xsl:when>
        <xsl:when test="parent::procedure/title">
          "<xsl:value-of select="title"/>"
        </xsl:when>
        <xsl:otherwise>
          "<xsl:value-of select="substring(normalize-space(preceding-sibling::step[1]), 1, 50)"/>..."
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="number-steps">
      <xsl:apply-templates select="parent::procedure/step[last()]" mode="count"/>
    </xsl:param>

    <result>
      <warning>Procedure <xsl:value-of select="$id"/> has <xsl:value-of select="$number-steps"/> steps.</warning>
      <expectation>Procedures may contain up to 10 steps.</expectation>
    </result>
  </xsl:template>

  <xsl:template match="step" mode="count">
    <xsl:number select="step"/>
  </xsl:template>

</xsl:stylesheet>